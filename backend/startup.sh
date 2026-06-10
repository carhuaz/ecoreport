#!/bin/bash
# Startup script for Azure App Service (Linux)
# Azure instala automáticamente las dependencias de requirements.txt

# Iniciar FastAPI con Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
