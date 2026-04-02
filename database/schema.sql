-- =============================================
-- Schema: Sistem de recomandare auto personalizată
-- =============================================

-- Tabel principal: mașinile disponibile
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    an INTEGER NOT NULL,
    pret FLOAT NOT NULL,
    tip_combustibil VARCHAR(20) NOT NULL,      -- benzina/diesel/electric/hybrid
    tip_caroserie VARCHAR(30) NOT NULL,         -- sedan/suv/hatchback/coupe/break
    putere_cp INTEGER,
    consum_mediu FLOAT,                         -- l/100km sau kWh/100km
    emisii_co2 FLOAT,
    lungime_mm INTEGER,
    latime_mm INTEGER,
    inaltime_mm INTEGER,
    volum_portbagaj INTEGER,                    -- litri
    numar_locuri INTEGER DEFAULT 5,
    rating_siguranta FLOAT CHECK (rating_siguranta BETWEEN 0 AND 5),
    rating_comfort FLOAT CHECK (rating_comfort BETWEEN 0 AND 5),
    rating_sport FLOAT CHECK (rating_sport BETWEEN 0 AND 5),
    rating_economie FLOAT CHECK (rating_economie BETWEEN 0 AND 5),
    rating_estetica FLOAT CHECK (rating_estetica BETWEEN 0 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel: sesiunile utilizatorilor
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
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
    recommended_car_ids VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index-uri pentru performanță
CREATE INDEX IF NOT EXISTS idx_cars_buget ON cars(pret);
CREATE INDEX IF NOT EXISTS idx_cars_combustibil ON cars(tip_combustibil);
CREATE INDEX IF NOT EXISTS idx_cars_caroserie ON cars(tip_caroserie);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON user_sessions(created_at);
