import ast
import sys
import io
import time
import traceback
import multiprocessing
from typing import Dict, Any, List, Optional
from app.core.config import settings

FORBIDDEN_CALLS = {
    "os.system", "os.popen", "os.spawn", "os.exec", "os.remove", "os.unlink", "os.rmdir",
    "subprocess.Popen", "subprocess.run", "subprocess.call", "subprocess.check_output",
    "shutil.rmtree", "shutil.move", "socket.socket"
}

FORBIDDEN_MODULES = {
    "subprocess", "socket", "pty", "commands", "ctypes"
}

class SecurityValidator(ast.NodeVisitor):
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
        # Detect calls like os.system(...)
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if func_name in FORBIDDEN_CALLS:
            self.errors.append(f"Function call '{func_name}' is blocked by sandbox safety policy.")
        self.generic_visit(node)

def _worker_execute(code_str: str, queue: multiprocessing.Queue):
    """Worker process function to safely execute Python code and capture output."""
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

        # Safe execution namespace with rich standard libraries
        safe_globals = {
            "__builtins__": __builtins__,
            "__name__": "__main__",
        }

        # Parse and execute
        parsed = ast.parse(code_str)
        
        # If the last statement is an expression, we can evaluate its value
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
    """
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

    # 2. Multiprocessing execution for strict timeout isolation
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_worker_execute, args=(code_str, queue))
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
            "stderr": "Execution terminated unexpectedly.",
            "return_value": None,
            "execution_time_ms": 0.0,
            "success": False
        }

    result["test_results"] = []
    return result
