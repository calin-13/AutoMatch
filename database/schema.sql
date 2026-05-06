-- =============================================
-- Schema: Sistem de recomandare auto personalizata
-- =============================================

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

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    test_version_completed INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LEGACY: pastrat pentru compat
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

-- NORMALIZED: header sesiune recomandare
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_snapshot JSON NOT NULL,
    scoring_method VARCHAR(20) NOT NULL DEFAULT 'ml',
    has_feedback_reranking BOOLEAN NOT NULL DEFAULT FALSE,
    total_candidates INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NORMALIZED: detaliu per masina recomandata
CREATE TABLE IF NOT EXISTS recommendation_items (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    car_id INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    score_total FLOAT NOT NULL,
    score_details JSON,
    CONSTRAINT uq_recitem_rec_rank UNIQUE (recommendation_id, rank)
);

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    car_id INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE,
    recommendation_id INTEGER REFERENCES recommendation_history(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN -1 AND 1),
    comment VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_feedback_user_car_rec UNIQUE (user_id, car_id, recommendation_id)
);

CREATE TABLE IF NOT EXISTS test_questions (
    id SERIAL PRIMARY KEY,
    version INTEGER NOT NULL,
    order_index INTEGER NOT NULL,
    text VARCHAR(500) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_question_version_order UNIQUE (version, order_index)
);

CREATE TABLE IF NOT EXISTS test_options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES test_questions(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    text VARCHAR(500) NOT NULL,
    scores JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS test_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES test_questions(id) ON DELETE CASCADE,
    option_id INTEGER NOT NULL REFERENCES test_options(id) ON DELETE CASCADE,
    test_version INTEGER NOT NULL,
    submission_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cars_pret ON cars(pret);
CREATE INDEX IF NOT EXISTS idx_cars_combustibil ON cars(tip_combustibil);
CREATE INDEX IF NOT EXISTS idx_cars_caroserie ON cars(tip_caroserie);
CREATE INDEX IF NOT EXISTS idx_cars_marca ON cars(marca);
CREATE INDEX IF NOT EXISTS idx_history_user ON recommendation_history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created ON recommendation_history(created_at);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_created ON recommendations(created_at);
CREATE INDEX IF NOT EXISTS idx_recitems_rec ON recommendation_items(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_recitems_car ON recommendation_items(car_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON recommendation_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_car ON recommendation_feedback(car_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rec ON recommendation_feedback(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_questions_version ON test_questions(version);
CREATE INDEX IF NOT EXISTS idx_options_question ON test_options(question_id);
CREATE INDEX IF NOT EXISTS idx_responses_user ON test_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_responses_submission ON test_responses(submission_id);
