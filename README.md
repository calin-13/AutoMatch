# AutoMatch - Smart Car Recommendation Engine

A web application that recommends the perfect car based on your physiological data and behavioral preferences.

## Overview

AutoMatch combines intelligent rule-based scoring with machine learning to deliver highly personalized car recommendations. The system analyzes your input through a comprehensive questionnaire and physiological data to identify the 5 best vehicle matches from an extensive catalog.

## Technology Stack

- **Frontend**: React (Vite)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Machine Learning**: XGBoost with scikit-learn
- **Hosting**: Vercel
- **API Documentation**: Swagger/OpenAPI

## Project Structure

```
AutoMatch/
├── backend/                  # FastAPI server
│   ├── api/                  # REST API endpoints
│   ├── models/               # Database models + Pydantic schemas
│   ├── services/             # Business logic (scoring, ML pipeline)
│   ├── data/                 # Datasets and ML training scripts
│   └── main.py               # FastAPI application entry point
├── frontend/                 # React application (Vite)
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page views
│   │   └── App.jsx           # Main application
│   └── package.json
├── database/                 # SQL schema and migrations
└── README.md
```

## Live Application

**AutoMatch is live and running:** [https://automatch-vercel.com](https://auto-match-seven.vercel.app)

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 15

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

- API available at: http://localhost:8000
- Swagger documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

### 2. Database Setup

```bash
createdb automatch
psql automatch < database/schema.sql
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Application available at: http://localhost:5173

## How Recommendations Work

### Stage 1: User Input

Users provide:
- Physiological Data: Height, weight, mobility constraints
- Practical Requirements: Budget range, daily kilometers, fuel type preference, cargo space, passenger count
- Behavioral Assessment: Mini psychological questionnaire

### Stage 2: Rule-Based Scoring

System generates a 5-dimensional user profile:
- **Comfort**: Preference for smooth, quiet, luxury rides
- **Sport**: Performance and driving engagement
- **Safety**: Safety features and reliability
- **Economy**: Fuel efficiency and operating costs
- **Aesthetics**: Design appeal and visual attractiveness

Each dimension is scored and normalized.

### Stage 3: ML Refinement

XGBoost model trained on historical user data learns complex preference patterns and refines recommendations with high accuracy.

### Output

- Top 5 personalized car recommendations
- Each with a compatibility score (0-100)
- Detailed reasoning for each recommendation

## API Endpoints

### Main Endpoints

- `POST /api/recommendations/` - Get personalized recommendations based on user profile
- `GET /api/cars/` - List all available cars in database
- `POST /api/profile/` - Create or update user profile
- `GET /api/profile/{user_id}` - Retrieve user profile
- `GET /api/profile/{user_id}/history` - Get recommendation history

See interactive documentation at `/docs`

## Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost/automatch
SECRET_KEY=your_secret_key_here
DEBUG=False
XGBOOST_MODEL_PATH=./models/xgboost_ranker.pkl
```

## Model Performance

Previously RandomForrest, but got better results with the XGBoost recommendation and it engine achieves:

See `backend/data/model_evaluation.md` for detailed performance analysis.

## Deployment

### Backend (Production)

```bash
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Frontend (Production)

```bash
cd frontend
npm run build
# dist/ folder ready for deployment
```

## System Architecture

```
┌─────────────────────────────────────┐
│   React Frontend (Vite)             │
│   - Questionnaire Form              │
│   - Results Display                 │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
├─────────────────────────────────────┤
│   ┌──────────────────────────────┐  │
│   │ Profile Scoring Service      │  │
│   │ - Rule-based 5D scoring      │  │
│   │ - Data validation            │  │
│   └──────────────────────────────┘  │
│                                     │
│   ┌──────────────────────────────┐  │
│   │ ML Ranking Service           │  │
│   │ - XGBoost model inference    │  │
│   │ - Score normalization        │  │
│   └──────────────────────────────┘  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   PostgreSQL 15                     │
│   - User profiles                   │
│   - Vehicle catalog                 │
│   - Recommendation history          │
└─────────────────────────────────────┘
```

## Dataset

- **Base Dataset**: Car Evaluation Dataset (~1700 records)
- **Extended Dataset**: ~2000-2500 records with synthetically generated data
- **Training Method**: Controlled generation to balance underrepresented vehicle categories

## Features

- Real-time personalized recommendations
- Hybrid rule-based + ML scoring system
- Responsive React UI with smooth animations
- Comprehensive REST API with Swagger documentation
- PostgreSQL data persistence
- XGBoost-powered ranking refinement
- User profile tracking and history

## Future Enhancements

- User ratings and feedback loop for model improvement
- Real-time market data integration
- Advanced filtering and comparison features
- Side-by-side vehicle comparison tool
- PDF report generation for recommendations
- Mobile app (React Native)
- Dealer API integrations

## Running Tests

```bash
cd backend
pytest
```

## License

MIT License - See LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Status**: Live & Operational
**Hosting**: Vercel
