from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base

DATABASE_URL = "postgresql://localhost:5432/auto_recommender"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Creează toate tabelele în baza de date."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency pentru FastAPI - oferă o sesiune DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
