import logging
from sqlalchemy.orm import Session
from app.models.question import InterviewQuestion
from app.models.mindmap import MindmapTopic
from app.seeds.seed_data import SEED_QUESTIONS
from app.services.mindmap_service import MINDMAP_DATA

logger = logging.getLogger(__name__)

def ensure_schema_columns(db: Session):
    """Safely adds phase and MCQ columns to interview_questions table if missing."""
    from sqlalchemy import text
    try:
        # Check SQLite or MySQL columns
        cols = [row[1] for row in db.execute(text("PRAGMA table_info(interview_questions);")).fetchall()]
        if cols:
            if "phase" not in cols:
                db.execute(text("ALTER TABLE interview_questions ADD COLUMN phase VARCHAR(50) DEFAULT 'basic';"))
            if "mcq_question" not in cols:
                db.execute(text("ALTER TABLE interview_questions ADD COLUMN mcq_question TEXT;"))
            if "mcq_options" not in cols:
                db.execute(text("ALTER TABLE interview_questions ADD COLUMN mcq_options JSON;"))
            if "mcq_correct_index" not in cols:
                db.execute(text("ALTER TABLE interview_questions ADD COLUMN mcq_correct_index INTEGER DEFAULT 0;"))
            if "mcq_explanation" not in cols:
                db.execute(text("ALTER TABLE interview_questions ADD COLUMN mcq_explanation TEXT;"))
            db.commit()
    except Exception as e:
        logger.warning(f"Schema column check: {e}")

def seed_database(db: Session):
    # Ensure any newly added schema columns exist in database
    ensure_schema_columns(db)

    # 1. Sync Questions by slug (creates new ones & updates existing ones with latest easy-to-understand explanations)
    existing_questions = {q.slug: q for q in db.query(InterviewQuestion).all()}
    new_questions = 0
    updated_questions = 0
    for q_data in SEED_QUESTIONS:
        slug = q_data["slug"]
        if slug not in existing_questions:
            question = InterviewQuestion(**q_data)
            db.add(question)
            new_questions += 1
        else:
            q = existing_questions[slug]
            for key, val in q_data.items():
                setattr(q, key, val)
            updated_questions += 1
    db.commit()
    logger.info(f"Questions sync: {new_questions} created, {updated_questions} updated with enhanced explanations.")

    # 2. Sync Mindmaps by slug
    existing_m_slugs = {m.slug for m in db.query(MindmapTopic.slug).all()}
    new_mindmaps = 0
    for m_data in MINDMAP_DATA:
        if m_data["slug"] not in existing_m_slugs:
            topic = MindmapTopic(**m_data)
            db.add(topic)
            new_mindmaps += 1
        else:
            t = db.query(MindmapTopic).filter(MindmapTopic.slug == m_data["slug"]).first()
            if t:
                t.mermaid_diagram = m_data.get("mermaid_diagram")
                t.nodes = m_data.get("nodes", [])
                t.description = m_data.get("description")
                t.title = m_data.get("title")
    db.commit()
    if new_mindmaps > 0:
        logger.info(f"Seeded {new_mindmaps} new mindmap topics.")
