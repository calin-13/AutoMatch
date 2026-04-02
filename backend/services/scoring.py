from models.schemas import UserInput, UserProfile


def calculate_rule_based_scores(user_input: UserInput) -> UserProfile:
    """
    Calculează profilul utilizatorului pe baza datelor fiziologice
    și a scorurilor din mini-testul comportamental.

    Returnează un UserProfile cu scoruri normalizate și categorii.
    """
    phys = user_input.physiological
    behav = user_input.behavioral

    # === Categorie buget ===
    if phys.buget < 5000:
        categorie_buget = "economic"
    elif phys.buget < 15000:
        categorie_buget = "mediu"
    elif phys.buget < 35000:
        categorie_buget = "premium"
    else:
        categorie_buget = "lux"

    # === Categorie utilizare (bazat pe km/zi) ===
    if phys.km_zi < 20:
        categorie_utilizare = "urban"
    elif phys.km_zi < 60:
        categorie_utilizare = "mixt"
    else:
        categorie_utilizare = "extraurban"

    # === Ajustări pe baza datelor fiziologice ===
    comfort_bonus = 0
    sport_bonus = 0
    siguranta_bonus = 0
    economie_bonus = 0
    estetica_bonus = 0

    # Persoanele înalte (>185cm) au nevoie de mai mult spațiu -> comfort+
    if phys.inaltime > 185:
        comfort_bonus += 2
    elif phys.inaltime < 165:
        # Persoanele mai scunde se descurcă bine cu mașini compacte
        economie_bonus += 1

    # Buget mic -> economie mai importantă
    if phys.buget < 10000:
        economie_bonus += 3
    elif phys.buget > 30000:
        estetica_bonus += 1
        comfort_bonus += 1

    # Mulți km/zi -> economie și comfort
    if phys.km_zi > 50:
        economie_bonus += 2
        comfort_bonus += 1
    elif phys.km_zi < 15:
        sport_bonus += 1

    # Tip combustibil preferințe
    if phys.tip_combustibil == "electric":
        economie_bonus += 2
        estetica_bonus += 1
    elif phys.tip_combustibil == "diesel":
        economie_bonus += 1
    elif phys.tip_combustibil == "benzina":
        sport_bonus += 1

    # === Combinare scoruri: behavioral + bonus-uri fiziologice ===
    raw_comfort = behav.comfort + comfort_bonus
    raw_sport = behav.sport + sport_bonus
    raw_siguranta = behav.siguranta + siguranta_bonus
    raw_economie = behav.economie + economie_bonus
    raw_estetica = behav.estetica + estetica_bonus

    # Normalizare la 0-100
    total = raw_comfort + raw_sport + raw_siguranta + raw_economie + raw_estetica
    if total == 0:
        total = 1  # Evitare împărțire la 0

    return UserProfile(
        comfort=round((raw_comfort / total) * 100, 1),
        sport=round((raw_sport / total) * 100, 1),
        siguranta=round((raw_siguranta / total) * 100, 1),
        economie=round((raw_economie / total) * 100, 1),
        estetica=round((raw_estetica / total) * 100, 1),
        categorie_buget=categorie_buget,
        categorie_utilizare=categorie_utilizare,
    )
