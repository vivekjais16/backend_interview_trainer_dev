"""
Tests for 1,000+ Question Bank Catalog Scale & Integrity:
- Total question volume >= 1,000
- 100% slug uniqueness
- Verification of cross questions, traps, best practices, and MCQs
- Coverage of Python data types, SQL, Docker, Redis, MongoDB, Kafka, Celery, K8s, and System Design
"""
import pytest
from app.seeds.seed_data import SEED_QUESTIONS
from app.models.question import QuestionCategory


def test_question_catalog_volume():
    """Verify the question bank contains over 1,000 comprehensive questions."""
    assert len(SEED_QUESTIONS) >= 1000, f"Expected at least 1,000 questions, got {len(SEED_QUESTIONS)}"


def test_slug_uniqueness():
    """Verify that every question has a unique slug."""
    slugs = [q["slug"] for q in SEED_QUESTIONS]
    assert len(slugs) == len(set(slugs)), f"Found duplicate slugs! Total: {len(slugs)}, Unique: {len(set(slugs))}"


def test_question_structure_and_cross_questions():
    """Verify each question has complete fields, deep cross questions, and verified MCQs."""
    for idx, q in enumerate(SEED_QUESTIONS):
        # Slug and Title
        assert q.get("slug"), f"Question at index {idx} missing slug"
        assert q.get("title"), f"Question '{q.get('slug')}' missing title"
        
        # Cross questions for deep interviewer grilling
        cross_qs = q.get("cross_questions", [])
        assert len(cross_qs) >= 2, f"Question '{q['slug']}' must have at least 2 cross questions"

        # Traps and Best practices
        assert len(q.get("common_traps", [])) >= 1, f"Question '{q['slug']}' missing common traps"
        assert len(q.get("best_practices", [])) >= 1, f"Question '{q['slug']}' missing best practices"

        # Career phase
        assert q.get("phase") in ["basic", "intermediate", "advanced", "architect"]

        # MCQ validation
        assert q.get("mcq_question"), f"Question '{q['slug']}' missing MCQ question"
        opts = q.get("mcq_options", [])
        assert len(opts) == 4, f"Question '{q['slug']}' must have exactly 4 MCQ options"
        assert 0 <= q.get("mcq_correct_index", -1) < 4, f"Question '{q['slug']}' has invalid correct index"
        assert q.get("mcq_explanation"), f"Question '{q['slug']}' missing MCQ explanation"


def test_domain_coverage():
    """Verify all major engineering domains are thoroughly represented."""
    categories = {q.get("category") for q in SEED_QUESTIONS}
    required_domains = [
        QuestionCategory.PYTHON_INTERNALS,
        QuestionCategory.POSTGRES_MYSQL,
        QuestionCategory.DOCKER_CONTAINERS,
        QuestionCategory.REDIS_CACHING,
        QuestionCategory.MONGODB_NOSQL,
        QuestionCategory.FASTAPI_ARCHITECTURE,
        QuestionCategory.KAFKA_MESSAGING,
        QuestionCategory.CELERY_RABBITMQ,
        QuestionCategory.KUBERNETES_DEVOPS,
        QuestionCategory.SYSTEM_DESIGN_MNC
    ]
    for domain in required_domains:
        assert domain.value in categories or domain in categories, f"Missing required domain: {domain}"
