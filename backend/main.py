from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.routes import router
from api.auth_routes import auth_router, limiter
from api.feedback_routes import feedback_router
from api.test_routes import test_router
from config import init_db, SessionLocal, CORS_ORIGINS
from services.test_service import seed_test_questions

app = FastAPI(
    title="Auto Recommender API",
    description="Sistem de recomandare auto personalizata",
    version="1.0.0",
)

# Rate limiter (slowapi)
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


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        result = seed_test_questions(db)
        print(f"Test questions seed: {result}")
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Auto Recommender API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
