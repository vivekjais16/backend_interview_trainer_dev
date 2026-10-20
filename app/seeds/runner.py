import logging
from sqlalchemy.orm import Session
from app.models.question import InterviewQuestion
from app.models.mindmap import MindmapTopic
from app.seeds.seed_data import SEED_QUESTIONS
from app.services.mindmap_service import MINDMAP_DATA

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    # 1. Sync Questions by slug
    existing_q_slugs = {q.slug for q in db.query(InterviewQuestion.slug).all()}
    new_questions = 0
    for q_data in SEED_QUESTIONS:
        if q_data["slug"] not in existing_q_slugs:
            question = InterviewQuestion(**q_data)
            db.add(question)
            new_questions += 1
    if new_questions > 0:
        db.commit()
        logger.info(f"Seeded {new_questions} new MNC interview questions.")
    else:
        logger.info(f"All {len(existing_q_slugs)} interview questions are up to date.")

    # 2. Sync Mindmaps by slug
    existing_m_slugs = {m.slug for m in db.query(MindmapTopic.slug).all()}
    new_mindmaps = 0
    for m_data in MINDMAP_DATA:
        if m_data["slug"] not in existing_m_slugs:
            topic = MindmapTopic(**m_data)
            db.add(topic)
            new_mindmaps += 1
        else:
            # Update mermaid diagram or nodes if updated
            t = db.query(MindmapTopic).filter(MindmapTopic.slug == m_data["slug"]).first()
            if t:
                t.mermaid_diagram = m_data.get("mermaid_diagram")
                t.nodes = m_data.get("nodes", [])
                t.description = m_data.get("description")
                t.title = m_data.get("title")
    db.commit()
    if new_mindmaps > 0:
        logger.info(f"Seeded {new_mindmaps} new mindmap topics.")
