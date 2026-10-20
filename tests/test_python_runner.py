from app.services.python_runner import run_python_code

def test_python_runner_basic_math():
    code = "x = 10\ny = 32\nprint(x + y)"
    res = run_python_code(code)
    assert res["success"] is True
    assert "42" in res["stdout"]
    assert res["execution_time_ms"] > 0

def test_python_runner_security_block_os():
    code = "import os\nos.system('echo hacked')"
    res = run_python_code(code)
    assert res["success"] is False
    assert "blocked by sandbox safety policy" in res["stderr"]

def test_python_runner_security_block_subprocess():
    code = "import subprocess\nsubprocess.run(['ls'])"
    res = run_python_code(code)
    assert res["success"] is False
    assert "restricted in sandbox for security" in res["stderr"]

def test_python_runner_timeout():
    code = "import time\nwhile True:\n    pass"
    res = run_python_code(code, timeout_seconds=1)
    assert res["success"] is False
    assert "timed out" in res["stderr"]
