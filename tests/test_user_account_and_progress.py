import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db, SessionLocal
from app.seeds.runner import seed_database
from app.models.user import Candidate

@pytest.fixture(scope="module", autouse=True)
def setup_db():
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

import uuid

def test_user_registration_and_login(client):
    uid = uuid.uuid4().hex[:6]
    username = f"alex_{uid}"
    email = f"alex_{uid}@faangprep.com"

    # 1. Register a new user
    reg_payload = {
        "username": username,
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Alex Mercer",
        "experience_years": 8,
        "experience_level": "senior",
        "target_role": "Staff Backend Engineer (Distributed Systems)",
        "target_companies": ["Google", "Meta", "Netflix"],
        "key_skills": ["Python", "Distributed Systems", "SQL", "Redis", "Kafka"]
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == username
    assert "Google" in reg_data["user"]["target_companies"]
    assert "Distributed Systems" in reg_data["user"]["key_skills"]

    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login with email
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Fetch profile (/auth/me)
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["full_name"] == "Alex Mercer"
    assert me_data["target_role"] == "Staff Backend Engineer (Distributed Systems)"

    # 4. Update profile (/auth/profile)
    update_res = client.put("/api/v1/auth/profile", headers=headers, json={
        "target_role": "Principal Systems Architect",
        "target_companies": ["Google", "Uber", "Stripe"],
        "key_skills": ["Distributed Systems", "Raft", "Python", "Redis", "Kafka"]
    })
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["target_role"] == "Principal Systems Architect"
    assert "Uber" in updated_data["target_companies"]

def test_user_mcq_progress_tracking(client):
    uid = uuid.uuid4().hex[:6]
    username = f"sarah_{uid}"

    # Register candidate for tracking
    reg_res = client.post("/api/v1/auth/register", json={
        "username": username,
        "password": "Password789!",
        "target_companies": ["Google", "Amazon"],
        "key_skills": ["Distributed Systems", "SQL"]
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = reg_res.json()["user"]["id"]

    # Record direct MCQ attempt
    attempt_res = client.post("/api/v1/user/mcq-attempt", headers=headers, json={
        "question_id": 1,
        "question_slug": "python-gil-concurrency",
        "domain": "Python Concurrency",
        "selected_index": 2,
        "is_correct": True,
        "time_spent_seconds": 45
    })
    assert attempt_res.status_code == 200
    att_data = attempt_res.json()
    assert att_data["is_correct"] is True
    assert att_data["candidate_id"] == user_id

    # Also verify via /questions/verify-mcq with bearer token
    verify_res = client.post("/api/v1/questions/verify-mcq", headers=headers, json={
        "question_id": 1,
        "selected_index": 2
    })
    assert verify_res.status_code == 200

    # Check user history
    history_res = client.get("/api/v1/user/history", headers=headers)
    assert history_res.status_code == 200
    h_data = history_res.json()
    assert h_data["mcq_attempts_count"] >= 1
    assert len(h_data["recent_mcq_attempts"]) >= 1

def test_user_personalized_recommendations(client):
    uid = uuid.uuid4().hex[:6]
    username = f"jordan_{uid}"

    # Register candidate targeting Google with Distributed Systems key skill
    reg_res = client.post("/api/v1/auth/register", json={
        "username": username,
        "password": "SecurePassword456!",
        "target_companies": ["Google", "Amazon"],
        "key_skills": ["Distributed Systems", "SQL", "Docker", "Redis"]
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch personalized recommendations
    rec_res = client.get("/api/v1/user/recommendations", headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()

    assert "overall_readiness_score" in rec_data
    assert "skills_breakdown" in rec_data
    assert len(rec_data["skills_breakdown"]) == 4
    assert len(rec_data["tailored_action_plan"]) > 0
    assert "Google" in rec_data["target_companies"]
    assert isinstance(rec_data["recommended_questions"], list)
    assert len(rec_data["recommended_questions"]) > 0
