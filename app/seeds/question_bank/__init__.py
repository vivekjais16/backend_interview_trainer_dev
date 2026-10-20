"""Aggregated Question Bank containing 1,000+ technical interview questions."""
from app.seeds.question_bank.python_internals import PYTHON_QUESTIONS
from app.seeds.question_bank.sql_database import SQL_QUESTIONS
from app.seeds.question_bank.docker_containers import DOCKER_QUESTIONS
from app.seeds.question_bank.redis_caching import REDIS_QUESTIONS
from app.seeds.question_bank.mongodb_nosql import MONGODB_QUESTIONS
from app.seeds.question_bank.fastapi_arch import FASTAPI_QUESTIONS
from app.seeds.question_bank.kafka_messaging import KAFKA_QUESTIONS
from app.seeds.question_bank.celery_queues import CELERY_QUESTIONS
from app.seeds.question_bank.kubernetes_devops import KUBERNETES_QUESTIONS
from app.seeds.question_bank.system_design import SYSTEM_DESIGN_QUESTIONS

CATALOG_QUESTIONS = (
    PYTHON_QUESTIONS +
    SQL_QUESTIONS +
    DOCKER_QUESTIONS +
    REDIS_QUESTIONS +
    MONGODB_QUESTIONS +
    FASTAPI_QUESTIONS +
    KAFKA_QUESTIONS +
    CELERY_QUESTIONS +
    KUBERNETES_QUESTIONS +
    SYSTEM_DESIGN_QUESTIONS
)
