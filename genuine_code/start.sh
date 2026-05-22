#!/bin/bash

echo "Starting Backend"
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8001 &

echo "Starting Rasa Action Server"
python -m rasa run actions --actions src.rasa.actions --port 5055 &

echo "Starting Rasa Core Server"
python -m rasa run --enable-api --cors "*" --model src/rasa/models --endpoints src/rasa/endpoints.yml --credentials src/rasa/credentials.yml --port 5005 &

echo "Waiting for services to initialize"
sleep 20

echo "Starting Chainlit UI"
cd src/frontend
python -m chainlit run app.py --port 7860 --host 0.0.0.0
