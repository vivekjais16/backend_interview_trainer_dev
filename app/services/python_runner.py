import ast
import sys
import io
import time
import traceback
import multiprocessing
try:
    import resource
except ImportError:
    resource = None
from typing import Dict, Any, List, Optional
from app.core.config import settings

FORBIDDEN_CALLS = {
    "os.system", "os.popen", "os.spawn", "os.exec", "os.remove", "os.unlink", "os.rmdir",
    "subprocess.Popen", "subprocess.run", "subprocess.call", "subprocess.check_output",
    "shutil.rmtree", "shutil.move", "socket.socket",
    "open", "eval", "exec", "compile", "__import__",
    "globals", "locals", "vars", "breakpoint", "input", "exit", "quit"
}

FORBIDDEN_MODULES = {
    "subprocess", "socket", "pty", "commands", "ctypes", "shutil",
    "posix", "resource", "signal", "inspect", "importlib",
    "multiprocessing", "threading", "pathlib", "tempfile",
    "pickle", "shelve", "webbrowser", "http", "urllib", "ftplib", "smtplib"
}

FORBIDDEN_NAMES = {
    "__builtins__", "eval", "exec", "compile", "__import__", "breakpoint"
}

class SecurityValidator(ast.NodeVisitor):
    """
    AST Security Scanner to eliminate code execution escapes, file tampering,
    subclass traversal (__subclasses__), and unauthorized OS module loading.
    """
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module in FORBIDDEN_MODULES:
                self.errors.append(f"Importing '{base_module}' is restricted in sandbox for security.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in FORBIDDEN_MODULES:
                self.errors.append(f"Importing from '{base_module}' is restricted in sandbox for security.")
        self.generic_visit(node)

    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if func_name in FORBIDDEN_CALLS:
            self.errors.append(f"Function call '{func_name}' is blocked by sandbox safety policy.")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Prevent subclass introspection & dunder escape attacks
        # e.g., ().__class__.__bases__[0].__subclasses__()
        if node.attr.startswith("__") and node.attr != "__name__":
            self.errors.append(f"Access to internal attribute '{node.attr}' is restricted for security.")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in FORBIDDEN_NAMES and isinstance(node.ctx, ast.Load):
            self.errors.append(f"Use of restricted identifier '{node.id}' is blocked.")
        self.generic_visit(node)


class ComplexityAnalyzer(ast.NodeVisitor):
    """
    AST Complexity Scanner analyzing Time Complexity (loops, searches, string copying)
    and Space Complexity (in-memory list allocations vs lazy generators).
    Generates Big-O optimization guidance to reduce O(N^2) -> O(N) or O(N) -> O(1).
    """
    def __init__(self, code_str: str):
        self.code_str = code_str
        self.current_loop_depth = 0
        self.max_loop_depth = 0
        self.has_recursion = False
        self.recursive_call_count = 0
        self.current_func_name = None
        self.has_lru_cache = False
        
        self.has_list_comp = False
        self.has_generator = False
        self.has_yield = False
        self.has_in_loop = False
        self.has_quadratic_string_concat = False
        self.has_nested_sort = False
        self.has_linear_list_search_in_loop = False
        
        self.time_bottlenecks = []
        self.space_bottlenecks = []
        self.suggestions = []

    def visit_FunctionDef(self, node):
        prev_func = self.current_func_name
        self.current_func_name = node.name
        
        for dec in node.decorator_list:
            dec_id = ""
            if isinstance(dec, ast.Name):
                dec_id = dec.id
            elif isinstance(dec, ast.Attribute):
                dec_id = dec.attr
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    dec_id = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    dec_id = dec.func.attr
            if "cache" in dec_id.lower():
                self.has_lru_cache = True

        self.generic_visit(node)
        self.current_func_name = prev_func

    def visit_For(self, node):
        self.current_loop_depth += 1
        if self.current_loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.current_loop_depth
            if self.current_loop_depth >= 2:
                self.time_bottlenecks.append(f"Nested for-loop on line {node.lineno} causes O(N^{self.current_loop_depth}) polynomial time.")

        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_While(self, node):
        self.current_loop_depth += 1
        if self.current_loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.current_loop_depth
            if self.current_loop_depth >= 2:
                self.time_bottlenecks.append(f"Nested while-loop on line {node.lineno} causes O(N^{self.current_loop_depth}) polynomial time.")

        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_Compare(self, node):
        if self.current_loop_depth >= 1:
            for op in node.ops:
                if isinstance(op, (ast.In, ast.NotIn)):
                    self.has_in_loop = True
                    self.time_bottlenecks.append(
                        f"Linear membership check ('val in collection') on line {node.lineno} inside a loop. If performed on a list, each lookup is O(N), escalating overall time to O(N²)."
                    )
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if self.current_loop_depth >= 1 and isinstance(node.op, ast.Add):
            self.has_quadratic_string_concat = True
            self.time_bottlenecks.append(
                f"Repeated concatenation ('+=') inside loop on line {node.lineno}. Python strings are immutable; each '+=' copies the buffer, resulting in O(N²) time."
            )
        self.generic_visit(node)

    def visit_Call(self, node):
        func_name = ""
        attr_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{attr_name}"
            else:
                func_name = attr_name

        if self.current_func_name and (func_name == self.current_func_name or attr_name == self.current_func_name):
            self.has_recursion = True
            self.recursive_call_count += 1

        if self.current_loop_depth >= 1:
            if attr_name in ("index", "count", "remove"):
                self.has_linear_list_search_in_loop = True
                self.time_bottlenecks.append(f"List method '.{attr_name}()' on line {node.lineno} is O(N). Calling it inside a loop results in O(N²) quadratic time.")
            elif attr_name in ("sort",) or func_name == "sorted":
                self.has_nested_sort = True
                self.time_bottlenecks.append(f"Sorting operation inside loop on line {node.lineno} causes O(N² log N) execution time.")

        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.has_list_comp = True
        self.space_bottlenecks.append(f"List comprehension on line {node.lineno} allocates all elements in RAM simultaneously (O(N) space).")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.has_generator = True
        self.generic_visit(node)

    def visit_Yield(self, node):
        self.has_yield = True
        self.generic_visit(node)

    def visit_YieldFrom(self, node):
        self.has_yield = True
        self.generic_visit(node)


def analyze_code_complexity(code_str: str) -> Dict[str, Any]:
    """Analyzes AST of Python code to estimate Big-O Time & Space complexity and provide optimization advice."""
    try:
        tree = ast.parse(code_str)
    except Exception:
        return {
            "time_complexity": "O(N)",
            "space_complexity": "O(1)",
            "time_bottlenecks": [],
            "space_bottlenecks": [],
            "suggestions": [],
            "optimal_time": "O(N)",
            "optimal_space": "O(1)"
        }

    analyzer = ComplexityAnalyzer(code_str)
    analyzer.visit(tree)

    # 1. Determine Time Complexity
    if analyzer.has_recursion and not analyzer.has_lru_cache and analyzer.recursive_call_count >= 2:
        time_comp = "O(2ⁿ) Exponential"
        optimal_time = "O(N)"
        analyzer.suggestions.append("🚀 Time Optimization: Add '@functools.lru_cache(None)' or memoization dictionary to cache subproblem results and reduce time from O(2ⁿ) to O(N).")
    elif analyzer.max_loop_depth >= 3:
        time_comp = "O(N³) Cubic"
        optimal_time = "O(N log N) or O(N)"
        analyzer.suggestions.append("🚀 Time Optimization: 3+ nested loops detected. Flatten iterations using a hash map lookup, sorting + two-pointer, or pre-computed matrix index.")
    elif analyzer.max_loop_depth == 2 or analyzer.has_in_loop or analyzer.has_linear_list_search_in_loop:
        time_comp = "O(N²) Quadratic"
        optimal_time = "O(N)"
        if analyzer.has_in_loop or analyzer.has_linear_list_search_in_loop:
            analyzer.suggestions.append("🚀 Time Optimization: Convert the target list to a 'set()' beforehand (e.g. 'lookup = set(my_list)'). Set membership tests take O(1) constant time instead of O(N) linear scans, reducing total time from O(N²) to O(N).")
        else:
            analyzer.suggestions.append("🚀 Time Optimization: Avoid nested loop comparisons. Pre-index items into a dictionary '{key: item}' for O(1) average lookup, achieving O(N) overall runtime.")
    elif analyzer.max_loop_depth == 1:
        time_comp = "O(N) Linear"
        optimal_time = "O(N)"
        if analyzer.has_quadratic_string_concat:
            analyzer.suggestions.append("🚀 Time Optimization: Replace 'str += chunk' inside loop with a list of chunks and `''.join(chunks)` at the end to prevent O(N²) string re-allocation.")
        else:
            analyzer.suggestions.append("✅ Optimal Time: O(N) linear iteration is standard for processing collections.")
    else:
        time_comp = "O(1) Constant"
        optimal_time = "O(1)"
        analyzer.suggestions.append("✅ Optimal Time: O(1) constant time execution without iteration loops.")

    # 2. Determine Space Complexity
    if analyzer.has_yield or (analyzer.has_generator and not analyzer.has_list_comp):
        space_comp = "O(1) Constant (Streaming)"
        optimal_space = "O(1)"
        analyzer.suggestions.append("✅ Optimal Space: Uses lazy generators / yield for O(1) constant memory streaming.")
    elif analyzer.has_list_comp or "[]" in code_str or "append(" in code_str:
        space_comp = "O(N) Linear (In-Memory)"
        optimal_space = "O(1)"
        analyzer.suggestions.append("💾 Space Optimization: If streaming large or unbounded datasets (e.g., millions of records or large files), replace list comprehension `[...]` with generator expression `(...)` or `yield` to reduce memory from O(N) to O(1) constant space.")
    else:
        space_comp = "O(1) Constant"
        optimal_space = "O(1)"

    return {
        "time_complexity": time_comp,
        "space_complexity": space_comp,
        "time_bottlenecks": analyzer.time_bottlenecks,
        "space_bottlenecks": analyzer.space_bottlenecks,
        "suggestions": analyzer.suggestions,
        "optimal_time": optimal_time,
        "optimal_space": optimal_space
    }


def _get_safe_builtins() -> Dict[str, Any]:
    """Whitelisted built-in functions; strictly excludes open, eval, exec, and blocks forbidden modules in imports."""
    safe_names = [
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
        'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter', 'float', 'format',
        'frozenset', 'hash', 'hex', 'id', 'int', 'isinstance', 'issubclass', 'iter',
        'len', 'list', 'map', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'print',
        'range', 'repr', 'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
        'tuple', 'type', 'zip', 'True', 'False', 'None',
        'ArithmeticError', 'AssertionError', 'AttributeError', 'BufferError',
        'Exception', 'IndexError', 'KeyError', 'LookupError', 'NameError',
        'OverflowError', 'RuntimeError', 'TypeError', 'ValueError', 'ZeroDivisionError'
    ]
    builtin_dict = {}
    import builtins
    for name in safe_names:
        if hasattr(builtins, name):
            builtin_dict[name] = getattr(builtins, name)

    # Controlled safe import function that blocks forbidden modules
    def _safe_import(name, *args, **kwargs):
        base_name = name.split('.')[0]
        if base_name in FORBIDDEN_MODULES:
            raise ImportError(f"Importing '{base_name}' is restricted in sandbox for security.")
        return builtins.__import__(name, *args, **kwargs)

    builtin_dict['__import__'] = _safe_import
    return builtin_dict


def _worker_execute(code_str: str, queue: multiprocessing.Queue, timeout_seconds: int = 5):
    """Worker process function with OS resource limits and safe execution namespace."""
    # Enforce kernel-level resource limits if available
    if resource is not None:
        try:
            # Maximum 256MB virtual memory
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
            # Block disk writes (0 bytes maximum file creation)
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        except Exception:
            pass

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()

    start_time = time.perf_counter()
    success = True
    return_val = None

    try:
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        # Safe execution namespace with sanitized builtins
        safe_globals = {
            "__builtins__": _get_safe_builtins(),
            "__name__": "__main__",
        }

        # Parse and execute
        parsed = ast.parse(code_str)
        
        # If the last statement is an expression, evaluate its return value
        if parsed.body and isinstance(parsed.body[-1], ast.Expr):
            last_expr = parsed.body.pop()
            exec_code = compile(parsed, filename="<interview_sandbox>", mode="exec")
            exec(exec_code, safe_globals)
            eval_code = compile(ast.Expression(last_expr.value), filename="<interview_sandbox>", mode="eval")
            return_val = eval(eval_code, safe_globals)
        else:
            exec_code = compile(parsed, filename="<interview_sandbox>", mode="exec")
            exec(exec_code, safe_globals)

    except Exception:
        success = False
        captured_stderr.write(traceback.format_exc())
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        queue.put({
            "stdout": captured_stdout.getvalue(),
            "stderr": captured_stderr.getvalue(),
            "return_value": str(return_val) if return_val is not None else None,
            "execution_time_ms": round(duration_ms, 2),
            "success": success
        })


def run_python_code(code_str: str, timeout_seconds: int = 5, test_cases: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Executes Python code in a sandboxed, AST-verified environment with strict timeout limits.
    Guards against tampering, filesystem operations, and process breakouts.
    """
    # 0. Size limitation (20 KB max code length)
    if len(code_str) > 20000:
        return {
            "stdout": "",
            "stderr": "Security Error: Code submission exceeds maximum allowed length of 20,000 characters.",
            "return_value": None,
            "execution_time_ms": 0.0,
            "success": False,
            "test_results": []
        }

    # 1. AST Safety Validation
    try:
        tree = ast.parse(code_str)
        validator = SecurityValidator()
        validator.visit(tree)
        if validator.errors:
            return {
                "stdout": "",
                "stderr": "\n".join(validator.errors),
                "return_value": None,
                "execution_time_ms": 0.0,
                "success": False,
                "test_results": []
            }
    except SyntaxError as e:
        return {
            "stdout": "",
            "stderr": f"SyntaxError: {e}",
            "return_value": None,
            "execution_time_ms": 0.0,
            "success": False,
            "test_results": []
        }

    # 2. Multiprocessing execution for strict timeout & resource isolation
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_worker_execute, args=(code_str, queue, timeout_seconds))
    proc.start()
    proc.join(timeout=timeout_seconds)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_seconds}s (Possible infinite loop or deadlock detected).",
            "return_value": None,
            "execution_time_ms": timeout_seconds * 1000.0,
            "success": False,
            "test_results": []
        }

    if not queue.empty():
        result = queue.get()
    else:
        result = {
            "stdout": "",
            "stderr": "Execution terminated unexpectedly or memory limit exceeded.",
            "return_value": None,
            "execution_time_ms": 0.0,
            "success": False
        }

    result["test_results"] = []
    result["complexity_analysis"] = analyze_code_complexity(code_str)
    return result

from app.contracts.execution import CodeExecutionContract

class PythonExecutionService(CodeExecutionContract):
    """
    Decoupled Python Execution Microservice Adapter.
    Implements CodeExecutionContract to isolate sandboxed execution from API transport.
    """
    def execute(self, code: str, timeout_seconds: int = 5) -> Dict[str, Any]:
        return run_python_code(code, timeout_seconds=timeout_seconds)

    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        return analyze_code_complexity(code)

python_execution_service = PythonExecutionService()
