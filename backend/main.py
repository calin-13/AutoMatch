from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.auth_routes import auth_router
from api.feedback_routes import feedback_router
from api.test_routes import test_router
from config import init_db, SessionLocal
from services.test_service import seed_test_questions

app = FastAPI(
    title="Auto Recommender API",
    description="Sistem de recomandare auto personalizata",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
