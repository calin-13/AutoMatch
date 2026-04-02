#!/bin/bash

touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/services/__init__.py
touch backend/data/__init__.py

pip install -r backend/requirements.txt

createdb auto_recommender 2>/dev/null
psql auto_recommender < database/schema.sql 2>/dev/null

echo "Setup complet."
echo "Pornire backend: cd backend && uvicorn main:app --reload"
