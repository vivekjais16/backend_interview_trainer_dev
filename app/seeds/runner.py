import logging
from sqlalchemy.orm import Session
from app.models.question import InterviewQuestion
from app.models.mindmap import MindmapTopic
from app.seeds.seed_data import SEED_QUESTIONS
from app.services.mindmap_service import MINDMAP_DATA

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    # 1. Seed Questions
    q_count = db.query(InterviewQuestion).count()
    if q_count == 0:
        logger.info(f"Seeding {len(SEED_QUESTIONS)} MNC interview questions...")
        for q_data in SEED_QUESTIONS:
            question = InterviewQuestion(**q_data)
            db.add(question)
        db.commit()
        logger.info("Questions seeded successfully.")
    else:
        logger.info(f"Database already has {q_count} questions. Skipping question seeding.")

    # 2. Seed Mindmaps
    m_count = db.query(MindmapTopic).count()
    if m_count == 0:
        logger.info(f"Seeding {len(MINDMAP_DATA)} mindmap topics...")
        for m_data in MINDMAP_DATA:
            topic = MindmapTopic(**m_data)
            db.add(topic)
        db.commit()
        logger.info("Mindmaps seeded successfully.")
    else:
        logger.info(f"Database already has {m_count} mindmap topics.")
