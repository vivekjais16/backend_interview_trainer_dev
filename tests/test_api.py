import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db, SessionLocal
from app.seeds.runner import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Python Backend" in res.text

def test_api_analytics_stats(client):
    res = client.get("/api/v1/analytics/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "experience_tracks" in data

def test_api_list_questions(client):
    res = client.get("/api/v1/questions")
    assert res.status_code == 200
    questions = res.json()
    assert isinstance(questions, list)
    assert len(questions) > 0

def test_api_questions_filter_experience(client):
    res = client.get("/api/v1/questions?experience_level=junior")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) > 0

def test_api_mindmaps(client):
    res = client.get("/api/v1/mindmaps")
    assert res.status_code == 200
    mindmaps = res.json()
    assert len(mindmaps) >= 3

def test_api_python_sandbox(client):
    payload = {"code": "print('MNC Interview Prep Ready')"}
    res = client.post("/api/v1/sandbox/python", json=payload)
    assert res.status_code == 200
    assert "MNC Interview Prep Ready" in res.json()["stdout"]

def test_api_sql_sandbox(client):
    payload = {"query": "SELECT COUNT(*) FROM products", "schema_name": "ecommerce"}
    res = client.post("/api/v1/sandbox/sql", json=payload)
    assert res.status_code == 200
    assert res.json()["success"] is True

def test_api_interview_session_and_turn(client):
    # 1. Create session
    session_res = client.post("/api/v1/interview/sessions", json={
        "session_title": "Google Bar Raiser Prep",
        "experience_level": "senior",
        "target_company": "Google"
    })
    assert session_res.status_code == 200
    session_id = session_res.json()["id"]

    # 2. Submit turn
    turn_res = client.post("/api/v1/interview/turns", json={
        "session_id": session_id,
        "candidate_response": "We use Redis distributed locks with Lua scripts to achieve atomic reservation and avoid race conditions.",
        "candidate_code": "def solve(): return 42"
    })
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert turn_data["score"] >= 0
    assert len(turn_data["cross_questions_asked"]) > 0
    assert "feedback" in turn_data

def test_api_phases(client):
    res = client.get("/api/v1/questions/phases")
    assert res.status_code == 200
    data = res.json()
    assert "phases" in data
    assert len(data["phases"]) == 3
    assert data["total_questions"] >= 20
    assert data["phases"][0]["id"] == "basic"
    assert data["phases"][1]["id"] == "intermediate"
    assert data["phases"][2]["id"] == "advanced"

def test_api_mcq_quiz_and_verify(client):
    # 1. Fetch MCQs for basic phase
    quiz_res = client.get("/api/v1/questions/mcq-quiz?phase=basic")
    assert quiz_res.status_code == 200
    items = quiz_res.json()
    assert len(items) >= 6
    first_q = items[0]
    assert "mcq_question" in first_q
    assert len(first_q["mcq_options"]) == 4

    # 2. Verify answer
    verify_res = client.post("/api/v1/questions/verify-mcq", json={
        "question_id": first_q["id"],
        "selected_index": 1
    })
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert "is_correct" in v_data
    assert "correct_index" in v_data
    assert "explanation" in v_data

def test_api_filter_by_phase(client):
    res = client.get("/api/v1/questions?phase=intermediate")
    assert res.status_code == 200
    qs = res.json()
    assert len(qs) >= 7
    for q in qs:
        assert q["phase"] == "intermediate"

