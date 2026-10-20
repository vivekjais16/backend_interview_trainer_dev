import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.python_runner import run_python_code
from app.services.sql_runner import run_sql_query

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_security_headers_present(client):
    """Verify essential security headers are applied to protect against XSS and clickjacking."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
    assert "Content-Security-Policy" in res.headers
    assert res.headers["referrer-policy"] == "strict-origin-when-cross-origin"

def test_python_sandbox_blocks_file_reading():
    """Verify open() is completely blocked in Python sandbox."""
    code = "with open('app/core/config.py') as f:\n    print(f.read())"
    res = run_python_code(code)
    assert res["success"] is False
    assert "blocked by sandbox safety policy" in res["stderr"] or "restricted" in res["stderr"]

def test_python_sandbox_blocks_introspection_escape():
    """Verify dunder attribute introspection (__subclasses__) is strictly blocked."""
    code = "sub = ().__class__.__bases__[0].__subclasses__()\nprint(len(sub))"
    res = run_python_code(code)
    assert res["success"] is False
    assert "restricted for security" in res["stderr"]

def test_python_sandbox_blocks_eval_exec():
    """Verify eval() and exec() are blocked from runtime builtins and AST."""
    code = "x = eval('1 + 1')"
    res = run_python_code(code)
    assert res["success"] is False
    assert "blocked" in res["stderr"]

def test_sql_sandbox_blocks_attach_and_pragma():
    """Verify SQLite cannot attach files or inspect internal schemas."""
    attach_query = "ATTACH DATABASE 'test.db' AS test_db;"
    res1 = run_sql_query(attach_query)
    assert res1["success"] is False
    assert "forbidden" in res1["error"]

    pragma_query = "PRAGMA database_list;"
    res2 = run_sql_query(pragma_query)
    assert res2["success"] is False
    assert "forbidden" in res2["error"]

def test_questions_content_cannot_be_tampered(client):
    """Verify questions cannot be modified, created, or deleted via public HTTP endpoints."""
    # Attempt POST to questions
    res1 = client.post("/api/v1/questions", json={"title": "Hacked Question"})
    assert res1.status_code == 405  # Method Not Allowed

    # Attempt DELETE to questions
    res2 = client.delete("/api/v1/questions/1")
    assert res2.status_code == 405  # Method Not Allowed

    # Attempt PUT to questions
    res3 = client.put("/api/v1/questions/1", json={"title": "Hacked Question"})
    assert res3.status_code == 405  # Method Not Allowed

def test_payload_limit_protection(client):
    """Verify that requests exceeding 512KB are rejected with 413 Payload Too Large."""
    huge_payload = {"code": "x = 1\n" * 100000}  # ~600KB
    res = client.post("/api/v1/sandbox/python", json=huge_payload)
    # Either 413 from middleware or 200 with code length error from sandbox
    if res.status_code == 200:
        assert res.json()["success"] is False
        assert "exceeds maximum allowed length" in res.json()["stderr"]
    else:
        assert res.status_code == 413
