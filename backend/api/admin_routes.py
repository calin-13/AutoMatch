import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc

from config import get_db
from models.database import (
    User, UserProfile as UserProfileDB, Recommendation, RecommendationItem,
    RecommendationFeedback, Car
)
from models.schemas import (
    AdminUserItem, AdminUsersResponse,
    AdminPlatformStats, AdminMLMetrics, AdminRecentFeedbackItem,
    PromoteRequest,
)
from services.auth_service import require_admin, get_current_user

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.get(
    "/stats",
    response_model=AdminPlatformStats,
    summary="Statistici globale platforma",
)
def platform_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_admins = db.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0
    total_recs = db.query(func.count(Recommendation.id)).scalar() or 0
    total_fbs = db.query(func.count(RecommendationFeedback.id)).scalar() or 0

    fb_pos = db.query(func.count(RecommendationFeedback.id)).filter(RecommendationFeedback.rating == 1).scalar() or 0
    fb_neg = db.query(func.count(RecommendationFeedback.id)).filter(RecommendationFeedback.rating == -1).scalar() or 0
    fb_neu = db.query(func.count(RecommendationFeedback.id)).filter(RecommendationFeedback.rating == 0).scalar() or 0

    # Top 10 masini cele mai recomandate (pe baza recommendation_items)
    top_rec_rows = (
        db.query(
            Car.id, Car.marca, Car.model,
            func.count(RecommendationItem.id).label("times_recommended"),
        )
        .join(RecommendationItem, RecommendationItem.car_id == Car.id)
        .group_by(Car.id, Car.marca, Car.model)
        .order_by(desc("times_recommended"))
        .limit(10)
        .all()
    )
    most_recommended = [
        {"car_id": r[0], "marca": r[1], "model": r[2], "times_recommended": int(r[3])}
        for r in top_rec_rows
    ]

    # Top 10 useri cei mai activi (recomandari + feedbacks)
    rec_count_subq = (
        db.query(Recommendation.user_id, func.count(Recommendation.id).label("rec_count"))
        .group_by(Recommendation.user_id)
        .subquery()
    )
    fb_count_subq = (
        db.query(RecommendationFeedback.user_id, func.count(RecommendationFeedback.id).label("fb_count"))
        .group_by(RecommendationFeedback.user_id)
        .subquery()
    )

    active_rows = (
        db.query(
            User.id, User.username,
            func.coalesce(rec_count_subq.c.rec_count, 0).label("rec_count"),
            func.coalesce(fb_count_subq.c.fb_count, 0).label("fb_count"),
        )
        .outerjoin(rec_count_subq, rec_count_subq.c.user_id == User.id)
        .outerjoin(fb_count_subq, fb_count_subq.c.user_id == User.id)
        .order_by(desc("rec_count"), desc("fb_count"))
        .limit(10)
        .all()
    )
    most_active = [
        {
            "user_id": r[0],
            "username": r[1],
            "recommendations": int(r[2]),
            "feedbacks": int(r[3]),
        }
        for r in active_rows
    ]

    return AdminPlatformStats(
        total_users=total_users,
        total_admins=total_admins,
        total_recommendations=total_recs,
        total_feedbacks=total_fbs,
        feedbacks_positive=fb_pos,
        feedbacks_negative=fb_neg,
        feedbacks_neutral=fb_neu,
        most_recommended_cars=most_recommended,
        most_active_users=most_active,
    )


@admin_router.get(
    "/users",
    response_model=AdminUsersResponse,
    summary="Lista tuturor utilizatorilor cu detalii",
)
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()

    rec_counts = dict(
        db.query(Recommendation.user_id, func.count(Recommendation.id))
        .group_by(Recommendation.user_id)
        .all()
    )
    fb_counts = dict(
        db.query(RecommendationFeedback.user_id, func.count(RecommendationFeedback.id))
        .group_by(RecommendationFeedback.user_id)
        .all()
    )

    items = []
    for u in users:
        profile = db.query(UserProfileDB).filter(UserProfileDB.user_id == u.id).first()
        has_profile = profile is not None
        profile_complete = False
        if profile is not None:
            profile_complete = all([
                profile.inaltime is not None,
                profile.greutate is not None,
                profile.buget is not None,
                profile.km_zi is not None,
                profile.tip_combustibil is not None,
                profile.has_completed_test,
            ])

        items.append(AdminUserItem(
            id=u.id,
            email=u.email,
            username=u.username,
            role=u.role,
            has_profile=has_profile,
            profile_complete=profile_complete,
            recommendations_count=int(rec_counts.get(u.id, 0)),
            feedbacks_count=int(fb_counts.get(u.id, 0)),
            created_at=u.created_at,
        ))

    return AdminUsersResponse(total=len(items), users=items)


@admin_router.delete(
    "/users/{user_id}",
    summary="Sterge un utilizator (cu cascade pe profil, recomandari, feedback)",
)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Nu te poti sterge pe tine insuti")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"Utilizator id={user_id} inexistent")

    db.delete(user)
    db.commit()
    return {"deleted": True, "user_id": user_id}


@admin_router.get(
    "/ml/metrics",
    summary="Metricile modelelor ML din ml/metrics.json (full)",
)
def ml_metrics(admin: User = Depends(require_admin)):
    backend_dir = Path(__file__).resolve().parent.parent
    metrics_path = backend_dir / "ml" / "metrics.json"

    if not metrics_path.exists():
        return {"has_metrics": False}

    try:
        with open(metrics_path) as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la citirea metrics.json: {e}")

    return {
        "has_metrics": True,
        "dataset": data.get("dataset"),
        "regression_comparison": data.get("regression_comparison"),
        "classification_comparison": data.get("classification_comparison"),
        "best_models": data.get("best_models"),
        "feature_importance": data.get("feature_importance_best_regressor"),
    }


@admin_router.get(
    "/ml/feature-importance",
    summary="Doar feature importance pentru graficul de top features",
)
def ml_feature_importance(admin: User = Depends(require_admin)):
    backend_dir = Path(__file__).resolve().parent.parent
    metrics_path = backend_dir / "ml" / "metrics.json"

    if not metrics_path.exists():
        return {"available": False, "features": []}

    with open(metrics_path) as f:
        data = json.load(f)

    fi = data.get("feature_importance_best_regressor", {})
    sorted_fi = sorted(fi.items(), key=lambda x: -x[1])
    return {
        "available": True,
        "best_model": data.get("best_models", {}).get("regressor", "unknown"),
        "features": [{"feature": k, "importance": v} for k, v in sorted_fi],
    }


@admin_router.get(
    "/ml/comparison",
    summary="Comparatie sintetica intre modele (pentru grafic)",
)
def ml_comparison(admin: User = Depends(require_admin)):
    backend_dir = Path(__file__).resolve().parent.parent
    metrics_path = backend_dir / "ml" / "metrics.json"

    if not metrics_path.exists():
        return {"available": False}

    with open(metrics_path) as f:
        data = json.load(f)

    reg = data.get("regression_comparison", {})
    clf = data.get("classification_comparison", {})

    regressors = []
    for name, m in reg.items():
        regressors.append({
            "model": name,
            "mae": m.get("mae"),
            "r2": m.get("r2"),
            "cv_r2_mean": m.get("cv_r2_mean"),
            "cv_r2_std": m.get("cv_r2_std"),
        })

    classifiers = []
    for name, m in clf.items():
        classifiers.append({
            "model": name,
            "accuracy": m.get("accuracy"),
            "f1": m.get("f1"),
            "cv_accuracy_mean": m.get("cv_accuracy_mean"),
            "cv_accuracy_std": m.get("cv_accuracy_std"),
        })

    return {
        "available": True,
        "best_models": data.get("best_models"),
        "regressors": regressors,
        "classifiers": classifiers,
    }


@admin_router.get(
    "/feedback/recent",
    response_model=list[AdminRecentFeedbackItem],
    summary="Ultimele feedback-uri din toata platforma",
)
def recent_feedback(
    limit: int = Query(default=50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RecommendationFeedback, User, Car)
        .join(User, User.id == RecommendationFeedback.user_id)
        .join(Car, Car.id == RecommendationFeedback.car_id)
        .order_by(RecommendationFeedback.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        AdminRecentFeedbackItem(
            id=fb.id,
            user_id=u.id,
            username=u.username,
            car_id=car.id,
            car_marca=car.marca,
            car_model=car.model,
            rating=fb.rating,
            comment=fb.comment,
            created_at=fb.created_at,
        )
        for fb, u, car in rows
    ]


@admin_router.post(
    "/promote",
    summary="Promoveaza un utilizator la rol admin",
)
def promote_to_admin(
    payload: PromoteRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.id == payload.user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail=f"Utilizator id={payload.user_id} inexistent")
    if target.role == "admin":
        return {"already_admin": True, "user_id": target.id, "username": target.username}

    target.role = "admin"
    db.commit()
    return {"promoted": True, "user_id": target.id, "username": target.username}


@admin_router.post(
    "/demote",
    summary="Retrage rolul de admin (devine user normal)",
)
def demote_from_admin(
    payload: PromoteRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.user_id == admin.id:
        raise HTTPException(status_code=400, detail="Nu te poti retrograda pe tine insuti")

    target = db.query(User).filter(User.id == payload.user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail=f"Utilizator id={payload.user_id} inexistent")

    target.role = "user"
    db.commit()
    return {"demoted": True, "user_id": target.id, "username": target.username}
