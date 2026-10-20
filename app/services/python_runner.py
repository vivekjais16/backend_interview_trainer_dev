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
    return result
