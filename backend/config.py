from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/auto_recommender"
SECRET_KEY = "carmatchai_secret_key_2024_licenta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
