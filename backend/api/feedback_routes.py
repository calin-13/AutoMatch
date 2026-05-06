from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from config import get_db
from models.database import (
    User, Car, RecommendationFeedback, RecommendationHistory
)
from models.schemas import (
    FeedbackCreate, FeedbackResponse, FeedbackHistoryItem,
    FeedbackStatsItem, FeedbackStatsResponse,
)
from services.auth_service import get_current_user
from services.feedback_service import aggregate_feedback_by_attribute

feedback_router = APIRouter(prefix="/api", tags=["feedback"])


@feedback_router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Trimite feedback pentru o masina recomandata",
)
def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == payload.car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail=f"Masina cu id={payload.car_id} nu exista")

    if payload.recommendation_id is not None:
        rec = (
            db.query(RecommendationHistory)
            .filter(
                RecommendationHistory.id == payload.recommendation_id,
                RecommendationHistory.user_id == current_user.id,
            )
            .first()
        )
        if rec is None:
            raise HTTPException(
                status_code=404,
                detail="Recomandarea referita nu exista sau nu apartine acestui utilizator",
            )

    existing = (
        db.query(RecommendationFeedback)
        .filter(
            RecommendationFeedback.user_id == current_user.id,
            RecommendationFeedback.car_id == payload.car_id,
            RecommendationFeedback.recommendation_id == payload.recommendation_id,
        )
        .first()
    )

    if existing is not None:
        existing.rating = payload.rating
        existing.comment = payload.comment
        db.commit()
        db.refresh(existing)
        return existing

    feedback = RecommendationFeedback(
        user_id=current_user.id,
        car_id=payload.car_id,
        recommendation_id=payload.recommendation_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@feedback_router.get(
    "/auth/feedback",
    response_model=list[FeedbackHistoryItem],
    summary="Istoricul feedback-urilor utilizatorului curent",
)
def get_my_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RecommendationFeedback, Car)
        .join(Car, Car.id == RecommendationFeedback.car_id)
        .filter(RecommendationFeedback.user_id == current_user.id)
        .order_by(RecommendationFeedback.created_at.desc())
        .all()
    )
    return [
        FeedbackHistoryItem(
            id=fb.id,
            car_id=car.id,
            car_marca=car.marca,
            car_model=car.model,
            car_an=car.an,
            rating=fb.rating,
            comment=fb.comment,
            recommendation_id=fb.recommendation_id,
            created_at=fb.created_at,
        )
        for fb, car in rows
    ]


@feedback_router.get(
    "/auth/feedback-summary",
    summary="Agregare feedback-ului utilizatorului pe atribute (marca, caroserie, combustibil)",
)
def get_my_feedback_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returneaza preferintele agregate ale user-ului. Util pentru afisare in profil
    ('Preferi BMW si SUV-uri, eviti diesel') si pentru explicarea re-ranking-ului.
    """
    return aggregate_feedback_by_attribute(db, current_user.id)


@feedback_router.delete(
    "/feedback/{feedback_id}",
    summary="Sterge un feedback propriu",
)
def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fb = (
        db.query(RecommendationFeedback)
        .filter(
            RecommendationFeedback.id == feedback_id,
            RecommendationFeedback.user_id == current_user.id,
        )
        .first()
    )
    if fb is None:
        raise HTTPException(status_code=404, detail="Feedback inexistent sau nu apartine utilizatorului")

    db.delete(fb)
    db.commit()
    return {"deleted": True, "id": feedback_id}


@feedback_router.get(
    "/feedback/stats",
    response_model=FeedbackStatsResponse,
    summary="Statistici globale de feedback (top liked + top disliked)",
)
def get_feedback_stats(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    total = db.query(func.count(RecommendationFeedback.id)).scalar() or 0

    likes_expr = func.sum(case((RecommendationFeedback.rating == 1, 1), else_=0)).label("likes")
    dislikes_expr = func.sum(case((RecommendationFeedback.rating == -1, 1), else_=0)).label("dislikes")
    neutral_expr = func.sum(case((RecommendationFeedback.rating == 0, 1), else_=0)).label("neutral")
    total_expr = func.count(RecommendationFeedback.id).label("total_per_car")

    base_query = (
        db.query(
            Car.id.label("car_id"),
            Car.marca,
            Car.model,
            likes_expr,
            dislikes_expr,
            neutral_expr,
            total_expr,
        )
        .join(RecommendationFeedback, RecommendationFeedback.car_id == Car.id)
        .group_by(Car.id, Car.marca, Car.model)
    )
    rows = base_query.all()

    items = []
    for row in rows:
        likes = int(row.likes or 0)
        dislikes = int(row.dislikes or 0)
        neutral = int(row.neutral or 0)
        total_per_car = int(row.total_per_car or 0)
        score = round((likes - dislikes) / total_per_car, 3) if total_per_car > 0 else 0.0
        items.append(
            FeedbackStatsItem(
                car_id=row.car_id,
                marca=row.marca,
                model=row.model,
                likes=likes,
                dislikes=dislikes,
                neutral=neutral,
                total=total_per_car,
                score=score,
            )
        )

    most_liked = sorted(items, key=lambda x: (x.score, x.likes), reverse=True)[:limit]
    most_disliked = sorted(items, key=lambda x: (x.score, -x.dislikes))[:limit]

    return FeedbackStatsResponse(
        total_feedbacks=total,
        most_liked=most_liked,
        most_disliked=most_disliked,
    )
