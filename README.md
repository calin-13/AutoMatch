# Sistem Web de Recomandare Auto Personalizată

Aplicație web care recomandă mașini utilizatorului pe baza datelor fiziologice/practice și a unui mini-test psihologic comportamental.

## Stack Tehnologic

- **Frontend**: React (Vite)
- **Backend**: FastAPI (Python)
- **Baza de date**: PostgreSQL 15
- **ML**: scikit-learn (Random Forest)

## Structura Proiectului

```
Licenta/
├── backend/           # FastAPI server
│   ├── api/           # Endpoint-uri REST
│   ├── models/        # Modele DB + Pydantic schemas
│   ├── services/      # Logica de business (scoring, ML)
│   └── data/          # Dataset-uri și scripturi ML
├── frontend/          # React app (Vite)
├── database/          # Schema SQL, migrări
└── README.md
```

## Setup Local

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API disponibil la: http://localhost:8000
Documentație Swagger: http://localhost:8000/docs

### 2. Baza de date
```bash
createdb auto_recommender
psql auto_recommender < database/schema.sql
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App disponibil la: http://localhost:5173

## Algoritm de Recomandare

1. **Input utilizator**: Date fiziologice + mini-test comportamental
2. **Scoring rule-based**: Generare profil pe 5 axe (comfort, sport, siguranță, economie, estetică)
3. **Model ML**: Random Forest care rafinează recomandările
4. **Output**: Top 5 mașini recomandate cu scor de potrivire
