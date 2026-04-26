import uuid
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from config import get_db
from models.database import (
    User, TestQuestion, TestOption, TestResponse, UserProfile as UserProfileDB
)
from models.schemas import (
    TestQuestionsResponse, TestQuestionResponse, TestOptionResponse,
    TestSubmitRequest, TestSubmitResponse, TestResponseHistoryItem,
)
from services.auth_service import get_current_user
from services.test_service import aggregate_scores_from_options, LATEST_VERSION

test_router = APIRouter(prefix="/api/test", tags=["test"])


@test_router.get(
    "/questions",
    response_model=TestQuestionsResponse,
    summary="Returneaza intrebarile testului (default: ultima versiune)",
)
def get_questions(
    version: Optional[int] = Query(default=None, description="Versiunea testului. Default: cea mai recenta"),
    db: Session = Depends(get_db),
):
    target_version = version if version is not None else LATEST_VERSION

    questions = (
        db.query(TestQuestion)
        .filter(TestQuestion.version == target_version, TestQuestion.is_active == True)
        .order_by(TestQuestion.order_index)
        .all()
    )

    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"Versiunea {target_version} a testului nu exista in DB. Ruleaza seed-ul.",
        )

    return TestQuestionsResponse(
        version=target_version,
        total=len(questions),
        questions=[
            TestQuestionResponse(
                id=q.id,
                order_index=q.order_index,
                text=q.text,
                options=[
                    TestOptionResponse(
                        id=opt.id,
                        order_index=opt.order_index,
                        text=opt.text,
                        scores=opt.scores or {},
                    )
                    for opt in q.options
                ],
            )
            for q in questions
        ],
    )


@test_router.post(
    "/submit",
    response_model=TestSubmitResponse,
    summary="Trimite raspunsurile la mini-test si actualizeaza profilul",
)
def submit_test(
    payload: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Salveaza fiecare raspuns ca rand in test_responses (audit trail).
    Calculeaza scorurile agregate pe cele 5 axe si le scrie in user_profiles.
    Marcheaza test-ul ca finalizat (has_completed_test=True).
    """
    # Valideaza ca toate question_id si option_id exista si apartin versiunii corecte
    question_ids = [a.question_id for a in payload.answers]
    option_ids = [a.option_id for a in payload.answers]

    questions = (
        db.query(TestQuestion)
        .filter(TestQuestion.id.in_(question_ids), TestQuestion.version == payload.version)
        .all()
    )
    questions_by_id = {q.id: q for q in questions}

    if len(questions_by_id) != len(set(question_ids)):
        raise HTTPException(
            status_code=400,
            detail=f"Una sau mai multe intrebari nu apartin versiunii {payload.version}",
        )

    options = (
        db.query(TestOption)
        .filter(TestOption.id.in_(option_ids))
        .all()
    )
    options_by_id = {o.id: o for o in options}

    if len(options_by_id) != len(set(option_ids)):
        raise HTTPException(status_code=400, detail="Una sau mai multe optiuni nu exista")

    # Verifica fiecare pereche (question, option) e valida
    for ans in payload.answers:
        opt = options_by_id.get(ans.option_id)
        if opt is None or opt.question_id != ans.question_id:
            raise HTTPException(
                status_code=400,
                detail=f"Optiunea {ans.option_id} nu apartine intrebarii {ans.question_id}",
            )

    # Sterge raspunsurile vechi ale userului pentru aceasta versiune (re-submit clean)
    db.query(TestResponse).filter(
        TestResponse.user_id == current_user.id,
        TestResponse.test_version == payload.version,
    ).delete()
    db.commit()

    # Insereaza raspunsuri noi
    submission_id = str(uuid.uuid4())
    selected_options = []
    for ans in payload.answers:
        response = TestResponse(
            user_id=current_user.id,
            question_id=ans.question_id,
            option_id=ans.option_id,
            test_version=payload.version,
            submission_id=submission_id,
        )
        db.add(response)
        selected_options.append(options_by_id[ans.option_id])

    # Calculeaza scorurile agregate
    scores = aggregate_scores_from_options(selected_options)

    # Updateaza profilul utilizatorului
    profile = (
        db.query(UserProfileDB)
        .filter(UserProfileDB.user_id == current_user.id)
        .first()
    )
    profile_updated = False
    if profile is not None:
        profile.score_comfort = scores["comfort"]
        profile.score_sport = scores["sport"]
        profile.score_siguranta = scores["siguranta"]
        profile.score_economie = scores["economie"]
        profile.score_estetica = scores["estetica"]
        profile.has_completed_test = True
        profile.test_version_completed = payload.version
        profile_updated = True

    db.commit()

    return TestSubmitResponse(
        submission_id=submission_id,
        version=payload.version,
        answered_count=len(payload.answers),
        aggregated_scores=scores,
        profile_updated=profile_updated,
    )


@test_router.get(
    "/my-responses",
    response_model=list[TestResponseHistoryItem],
    summary="Istoricul submisiilor de test ale utilizatorului curent",
)
def get_my_responses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(TestResponse, TestOption)
        .join(TestOption, TestOption.id == TestResponse.option_id)
        .filter(TestResponse.user_id == current_user.id)
        .order_by(TestResponse.created_at.desc())
        .all()
    )

    # Grupeaza pe submission_id
    by_submission = defaultdict(lambda: {"options": [], "version": None, "submitted_at": None})
    for resp, opt in rows:
        b = by_submission[resp.submission_id]
        b["options"].append(opt)
        b["version"] = resp.test_version
        if b["submitted_at"] is None or resp.created_at > b["submitted_at"]:
            b["submitted_at"] = resp.created_at

    result = []
    for sub_id, data in by_submission.items():
        scores = aggregate_scores_from_options(data["options"])
        result.append(
            TestResponseHistoryItem(
                submission_id=sub_id,
                version=data["version"],
                answered_count=len(data["options"]),
                aggregated_scores=scores,
                submitted_at=data["submitted_at"],
            )
        )

    result.sort(key=lambda x: x.submitted_at, reverse=True)
    return result
