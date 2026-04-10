from app.db.database import SessionLocal
from app.models.skill import Skill
from app.services import skill as skill_crud


ALLOWED_SKILLS = [
    "Yutori Verifier",
    "Yutori Annotation",
    "Robotics Annotation",
    "Development",
    "Robotics Data Collection",
    "Data Labeling",
    "Quality Review",
    "Smart Factory Development",
]


def seed_skills():
    db = SessionLocal()
    try:
        # Keep the dropdown catalog restricted to the approved skill list.
        db.query(Skill).filter(~Skill.name.in_(ALLOWED_SKILLS)).delete(synchronize_session=False)

        for skill_name in ALLOWED_SKILLS:
            skill_crud.create_skill_if_not_exists(db, skill_name)

        db.commit()
        print(f"Seeded {len(ALLOWED_SKILLS)} approved skills")
    finally:
        db.close()


if __name__ == "__main__":
    seed_skills()
