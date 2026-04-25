-- =============================================
-- Schema: Sistem de recomandare auto personalizata
-- =============================================

-- Catalog masini
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    an INTEGER NOT NULL,
    pret FLOAT NOT NULL,
    tip_combustibil VARCHAR(20) NOT NULL,
    tip_caroserie VARCHAR(30) NOT NULL,
    putere_cp INTEGER,
    consum_mediu FLOAT,
    emisii_co2 FLOAT,
    lungime_mm INTEGER,
    latime_mm INTEGER,
    inaltime_mm INTEGER,
    volum_portbagaj INTEGER,
    numar_locuri INTEGER DEFAULT 5,
    rating_siguranta FLOAT CHECK (rating_siguranta BETWEEN 0 AND 5),
    rating_comfort FLOAT CHECK (rating_comfort BETWEEN 0 AND 5),
    rating_sport FLOAT CHECK (rating_sport BETWEEN 0 AND 5),
    rating_economie FLOAT CHECK (rating_economie BETWEEN 0 AND 5),
    rating_estetica FLOAT CHECK (rating_estetica BETWEEN 0 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Utilizatori (autentificare)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profil persistent: 1-to-1 cu users (date ergonomice + ultimele scoruri test)
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    inaltime FLOAT,
    greutate FLOAT,
    buget FLOAT,
    km_zi FLOAT,
    tip_combustibil VARCHAR(20),
    score_comfort FLOAT,
    score_sport FLOAT,
    score_siguranta FLOAT,
    score_economie FLOAT,
    score_estetica FLOAT,
    has_completed_test BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Istoric recomandari per utilizator
CREATE TABLE IF NOT EXISTS recommendation_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    inaltime FLOAT,
    greutate FLOAT,
    buget FLOAT,
    km_zi FLOAT,
    tip_combustibil VARCHAR(20),
    score_comfort FLOAT,
    score_sport FLOAT,
    score_siguranta FLOAT,
    score_economie FLOAT,
    score_estetica FLOAT,
    recommended_cars VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru performanta
CREATE INDEX IF NOT EXISTS idx_cars_pret ON cars(pret);
CREATE INDEX IF NOT EXISTS idx_cars_combustibil ON cars(tip_combustibil);
CREATE INDEX IF NOT EXISTS idx_cars_caroserie ON cars(tip_caroserie);
CREATE INDEX IF NOT EXISTS idx_history_user ON recommendation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created ON recommendation_history(created_at);
