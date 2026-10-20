import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.python_runner import analyze_code_complexity

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_complexity_nested_loops():
    code = """
for i in range(10):
    for j in range(10):
        print(i, j)
"""
    result = analyze_code_complexity(code)
    assert "Quadratic" in result["time_complexity"]
    assert len(result["time_bottlenecks"]) > 0
    assert any("O(N²)" in s or "hash map" in s or "dictionary" in s for s in result["suggestions"])

def test_complexity_membership_in_loop():
    code = """
items = [1, 2, 3]
other = [2, 3, 4]
for x in items:
    if x in other:
        print(x)
"""
    result = analyze_code_complexity(code)
    assert "Quadratic" in result["time_complexity"]
    assert any("set" in s for s in result["suggestions"])

def test_complexity_generator_constant_space():
    code = """
def stream_data(n):
    for i in range(n):
        yield i * 2
"""
    result = analyze_code_complexity(code)
    assert "O(1)" in result["space_complexity"]

def test_complexity_list_comp_linear_space():
    code = """
data = [x * 2 for x in range(1000)]
"""
    result = analyze_code_complexity(code)
    assert "O(N)" in result["space_complexity"]
    assert any("generator" in s for s in result["suggestions"])

def test_complexity_api_sandbox(client):
    code = """
nums = [1, 2, 3, 4, 5]
sq = [x*x for x in nums]
print(sq)
"""
    res = client.post("/api/v1/sandbox/python", json={"code": code})
    assert res.status_code == 200
    data = res.json()
    assert "complexity_analysis" in data
    c = data["complexity_analysis"]
    assert "time_complexity" in c
    assert "space_complexity" in c
    assert "suggestions" in c
    assert len(c["suggestions"]) > 0
