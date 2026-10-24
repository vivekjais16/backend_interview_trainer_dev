import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_llm_presets(client):
    res = client.get("/api/v1/llm/presets")
    assert res.status_code == 200
    presets = res.json()
    assert isinstance(presets, list)
    assert len(presets) >= 4
    assert any("Rate Limiter" in p["title"] for p in presets)
    assert any("Python GIL" in p["title"] for p in presets)

def test_llm_ask_comprehensive_custom_problem(client):
    payload = {
        "question": "How do I resolve a split-brain condition in a 5-node distributed cluster when 2 nodes are partitioned off?",
        "mode": "comprehensive",
        "target_company": "Google"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 100
    assert "provider" in data
    assert "action_chips" in data
    assert len(data["action_chips"]) > 0

def test_llm_ask_code_solution(client):
    payload = {
        "question": "Implement an LRU Cache with O(1) get and put operations",
        "mode": "code_solution",
        "target_company": "Amazon"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "```python" in data["answer"]
    assert data["mode"] == "code_solution"

def test_llm_ask_eli5(client):
    payload = {
        "question": "Explain how database indexing with B+ Trees works",
        "mode": "eli5",
        "target_company": "Meta"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Explain Like I'm 5" in data["answer"] or "Analogy" in data["answer"]

def test_llm_ask_system_design(client):
    payload = {
        "question": "Design a real-time collaborative document editing service like Google Docs",
        "mode": "system_design",
        "target_company": "Google"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Architecture" in data["answer"] or "System Design" in data["answer"]

def test_llm_ask_with_prompt_alias(client):
    payload = {
        "prompt": "python",
        "mode": "comprehensive"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "answer_markdown" in data
    assert "model_used" in data
    assert len(data["key_invariants"]) > 0
    assert len(data["distractor_traps"]) > 0

def test_llm_ask_with_enterprise_target_company(client):
    payload = {
        "question": "What are microservices best practices in enterprise cloud migrations?",
        "prompt": "What are microservices best practices in enterprise cloud migrations?",
        "mode": "comprehensive",
        "target_company": "Capgemini"
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 50

def test_llm_ask_empty_returns_400(client):
    payload = {
        "prompt": "   ",
        "question": ""
    }
    res = client.post("/api/v1/llm/ask", json=payload)
    assert res.status_code == 400
    err = res.json()
    assert "detail" in err
    assert "Please enter a technical question" in err["detail"]

