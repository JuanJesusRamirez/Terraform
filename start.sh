#!/bin/sh

# Create necessary directories
mkdir -p backend/app/agents/sources/outlook-2025

# Iniciar uvicorn en segundo plano
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 &

# Volver al directorio principal y luego ir al directorio frontend
cd ..
cd frontend
streamlit run app.py