from sqlalchemy.orm import Session
from models.database import TestQuestion, TestOption


# Versiunea 1 - cele 5 intrebari originale
QUESTIONS_V1 = [
    {
        "text": "Cand conduci pe autostrada, ce este cel mai important pentru tine?",
        "options": [
            {"text": "Sa ma simt in siguranta", "scores": {"siguranta": 3, "comfort": 1}},
            {"text": "Sa simt puterea motorului", "scores": {"sport": 3, "estetica": 1}},
            {"text": "Sa consum cat mai putin", "scores": {"economie": 3, "comfort": 1}},
            {"text": "Sa am un drum lin si silentios", "scores": {"comfort": 3, "siguranta": 1}},
        ],
    },
    {
        "text": "Ce aspect al unei masini te atrage primul?",
        "options": [
            {"text": "Designul exterior", "scores": {"estetica": 3, "sport": 1}},
            {"text": "Spatiul interior", "scores": {"comfort": 3, "siguranta": 1}},
            {"text": "Consumul si costurile de intretinere", "scores": {"economie": 3, "siguranta": 1}},
            {"text": "Performantele tehnice", "scores": {"sport": 3, "estetica": 1}},
        ],
    },
    {
        "text": "Cum ai descrie stilul tau de condus?",
        "options": [
            {"text": "Prudent si atent", "scores": {"siguranta": 3, "economie": 1}},
            {"text": "Sportiv si dinamic", "scores": {"sport": 3, "estetica": 1}},
            {"text": "Relaxat si confortabil", "scores": {"comfort": 3, "economie": 1}},
            {"text": "Eficient si practic", "scores": {"economie": 3, "comfort": 1}},
        ],
    },
    {
        "text": "Daca ai avea buget nelimitat, ce masina ai alege?",
        "options": [
            {"text": "Un SUV mare si sigur (Volvo XC90)", "scores": {"siguranta": 3, "comfort": 2}},
            {"text": "Un supercar (Ferrari, Lamborghini)", "scores": {"sport": 3, "estetica": 2}},
            {"text": "O limuzina de lux (Mercedes S-Class)", "scores": {"comfort": 3, "estetica": 2}},
            {"text": "O masina electrica premium (Tesla)", "scores": {"economie": 2, "sport": 2, "estetica": 1}},
        ],
    },
    {
        "text": "Ce faci de obicei in weekend cu masina?",
        "options": [
            {"text": "Plimbari scurte prin oras", "scores": {"economie": 3, "comfort": 1}},
            {"text": "Drumuri lungi, excursii", "scores": {"comfort": 3, "siguranta": 1}},
            {"text": "Merg pe trasee montane/off-road", "scores": {"sport": 2, "siguranta": 2}},
            {"text": "O folosesc rar, prefer transportul public", "scores": {"economie": 3, "estetica": 1}},
        ],
    },
]


# Versiunea 2 - 15 intrebari (cele 5 din v1 + 10 noi, validate ca relevante pt preferinte auto)
QUESTIONS_V2 = QUESTIONS_V1 + [
    {
        "text": "Pe ce drumuri conduci cel mai des?",
        "options": [
            {"text": "Oras aglomerat (multe semafoare, parcari)", "scores": {"economie": 2, "comfort": 1}},
            {"text": "Mixt - oras + autostrada", "scores": {"comfort": 2, "siguranta": 1}},
            {"text": "Mai mult autostrada / drumuri lungi", "scores": {"comfort": 3, "siguranta": 1}},
            {"text": "Drumuri proaste, off-road, sat", "scores": {"siguranta": 2, "sport": 1}},
        ],
    },
    {
        "text": "Cat de des accelerezi rapid de la stop?",
        "options": [
            {"text": "Aproape niciodata - pornesc lin", "scores": {"economie": 3, "comfort": 1}},
            {"text": "Doar cand sunt grabit", "scores": {"economie": 2, "sport": 1}},
            {"text": "Destul de des, imi place senzatia", "scores": {"sport": 3, "estetica": 1}},
            {"text": "Mereu - asa cred ca trebuie condus", "scores": {"sport": 3, "estetica": 2}},
        ],
    },
    {
        "text": "Cate bagaje sau echipament transporti de obicei?",
        "options": [
            {"text": "Aproape niciodata nimic in plus", "scores": {"sport": 2, "estetica": 1}},
            {"text": "Cumparaturile saptamanale", "scores": {"comfort": 2, "economie": 1}},
            {"text": "Bagaje de vacanta, copii, echipament sport", "scores": {"comfort": 2, "siguranta": 2}},
            {"text": "Mereu transport multe lucruri (lucru, hobby)", "scores": {"comfort": 3, "economie": 1}},
        ],
    },
    {
        "text": "Pasagerii tai obisnuiti sunt:",
        "options": [
            {"text": "Doar eu", "scores": {"sport": 2, "estetica": 2}},
            {"text": "Eu si partener/a (ocazional)", "scores": {"comfort": 2, "estetica": 1, "sport": 1}},
            {"text": "Familie cu copii", "scores": {"siguranta": 3, "comfort": 2}},
            {"text": "Colegi / prieteni la drumuri lungi", "scores": {"comfort": 3, "siguranta": 1}},
        ],
    },
    {
        "text": "Cat te intereseaza tehnologia auto (apps, asistenta, autopilot)?",
        "options": [
            {"text": "Foarte mult - vreau cele mai noi feature-uri", "scores": {"estetica": 2, "siguranta": 1, "economie": 1}},
            {"text": "Moderat - utile dar nu esentiale", "scores": {"comfort": 2, "siguranta": 1, "economie": 1}},
            {"text": "Putin - prefer simplitatea", "scores": {"economie": 2, "comfort": 1}},
            {"text": "Deloc - imi place mecanic, fara electronice", "scores": {"sport": 2, "economie": 1}},
        ],
    },
    {
        "text": "Cati ani planuiesti sa pastrezi masina?",
        "options": [
            {"text": "1-3 ani - imi place schimbarea", "scores": {"estetica": 3, "sport": 1}},
            {"text": "4-7 ani - durata medie", "scores": {"comfort": 2, "estetica": 1, "siguranta": 1}},
            {"text": "8+ ani - pana se uzeaza", "scores": {"economie": 3, "siguranta": 1}},
            {"text": "Cat rezista - nu ma gandesc la asta", "scores": {"economie": 2, "comfort": 1}},
        ],
    },
    {
        "text": "Cat e bugetul tau anual pentru combustibil?",
        "options": [
            {"text": "Foarte mic - incerc sa economisesc maxim", "scores": {"economie": 3}},
            {"text": "Mediu - accept un consum rezonabil", "scores": {"economie": 2, "comfort": 1}},
            {"text": "Mai mare - prioritizez performanta", "scores": {"sport": 2, "comfort": 1}},
            {"text": "Nu e o preocupare pentru mine", "scores": {"sport": 2, "estetica": 1, "comfort": 1}},
        ],
    },
    {
        "text": "Cum ai descrie atitudinea ta fata de service-ul auto?",
        "options": [
            {"text": "Platesc oricat pentru calitate", "scores": {"comfort": 2, "siguranta": 2}},
            {"text": "Caut cel mai ieftin care e ok", "scores": {"economie": 3, "comfort": 1}},
            {"text": "Fac eu mici reparatii daca pot", "scores": {"economie": 2, "sport": 1}},
            {"text": "Doar la nevoie, evit cat pot", "scores": {"economie": 2, "estetica": 1}},
        ],
    },
    {
        "text": "La un drum de 500 km, ce e cel mai important pentru tine?",
        "options": [
            {"text": "Sa ajung repede", "scores": {"sport": 3, "comfort": 1}},
            {"text": "Sa ajung odihnit", "scores": {"comfort": 3, "siguranta": 1}},
            {"text": "Sa consum cat mai putin", "scores": {"economie": 3, "comfort": 1}},
            {"text": "Sa ma bucur de drum", "scores": {"sport": 2, "estetica": 2}},
        ],
    },
    {
        "text": "La ce zgomot al motorului preferi?",
        "options": [
            {"text": "Cat mai silentios posibil", "scores": {"comfort": 3, "economie": 1}},
            {"text": "Discret, dar prezent", "scores": {"comfort": 2, "estetica": 1}},
            {"text": "Sportiv, placut auzit", "scores": {"sport": 3, "estetica": 1}},
            {"text": "Nu ma deranjeaza zgomotul motorului", "scores": {"economie": 2, "sport": 1}},
        ],
    },
]


VERSIONS = {
    1: QUESTIONS_V1,
    2: QUESTIONS_V2,
}

LATEST_VERSION = 2


def seed_test_questions(db: Session) -> dict:
    """Insereaza versiunile de test in DB daca nu exista deja. Idempotent."""
    seeded = {"v1_inserted": 0, "v2_inserted": 0, "skipped_existing": 0}

    for version, questions in VERSIONS.items():
        existing = db.query(TestQuestion).filter(TestQuestion.version == version).count()
        if existing == len(questions):
            seeded["skipped_existing"] += existing
            continue
        if existing > 0:
            # Versiune partial inserata - sterge si reinserează curat
            db.query(TestQuestion).filter(TestQuestion.version == version).delete()
            db.commit()

        for idx, q in enumerate(questions, start=1):
            question = TestQuestion(
                version=version,
                order_index=idx,
                text=q["text"],
            )
            db.add(question)
            db.flush()  # ca sa avem question.id

            for opt_idx, opt in enumerate(q["options"], start=1):
                option = TestOption(
                    question_id=question.id,
                    order_index=opt_idx,
                    text=opt["text"],
                    scores=opt["scores"],
                )
                db.add(option)

            seeded[f"v{version}_inserted"] += 1

        db.commit()

    return seeded


def aggregate_scores_from_options(options: list) -> dict:
    """Aduna scorurile pe cele 5 axe din optiunile selectate."""
    totals = {"comfort": 0, "sport": 0, "siguranta": 0, "economie": 0, "estetica": 0}
    for opt in options:
        for axis, value in (opt.scores or {}).items():
            if axis in totals:
                totals[axis] += value
    return totals
