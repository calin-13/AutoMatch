import logging
import sys
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.routes import router
from api.auth_routes import auth_router, limiter
from api.feedback_routes import feedback_router
from api.test_routes import test_router
from api.admin_routes import admin_router
from config import init_db, SessionLocal, CORS_ORIGINS, get_db
from models.database import Car, User, Recommendation, RecommendationFeedback
from services.test_service import seed_test_questions
from services.ml_service import is_available as ml_is_available

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("auto_recommender")


app = FastAPI(
    title="Auto Recommender API",
    description="Sistem de recomandare auto personalizata",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(feedback_router)
app.include_router(test_router)
app.include_router(admin_router)


@app.on_event("startup")
def startup():
    logger.info("Auto Recommender API starting up...")
    init_db()
    logger.info("DB tables initialized")
    db = SessionLocal()
    try:
        result = seed_test_questions(db)
        logger.info(f"Test questions seed: {result}")
    finally:
        db.close()
    logger.info("Startup complete")


@app.get("/")
def root():
    return {"message": "Auto Recommender API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/version")
def version_info(db: Session = Depends(get_db)):
    """Status componente (util pentru debug si demo)."""
    backend_dir = Path(__file__).resolve().parent
    metrics_exists = (backend_dir / "ml" / "metrics.json").exists()

    total_cars = db.query(func.count(Car.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_recs = db.query(func.count(Recommendation.id)).scalar() or 0
    total_fbs = db.query(func.count(RecommendationFeedback.id)).scalar() or 0

    return {
        "api_version": "1.0.0",
        "components": {
            "database": "connected",
            "ml_models": "loaded" if ml_is_available() else "unavailable",
            "shap_explainability": "enabled" if ml_is_available() else "disabled",
            "rate_limiter": "active",
            "ml_metrics_file": "present" if metrics_exists else "missing",
        },
        "data": {
            "cars": total_cars,
            "users": total_users,
            "recommendations": total_recs,
            "feedbacks": total_fbs,
        },
        "features": {
            "user_profile": True,
            "feedback_system": True,
            "feedback_reranking": True,
            "behavioral_test_versioning": True,
            "diversity_mmr": True,
            "admin_dashboard": True,
        },
    }
