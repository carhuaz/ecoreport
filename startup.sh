#!/bin/bash
set -e

echo "=== Instalando dependencias de Python ==="
pip install -r requirements.txt

echo "=== Iniciando servidor ==="
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
