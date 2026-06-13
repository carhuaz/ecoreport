import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, reportes, usuarios, cuadrillas, estadisticas, mapa

app = FastAPI(
    title="EcoReport API",
    description="API REST para el sistema de reportes ambientales",
    version="1.0.0"
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)
app.include_router(cuadrillas.router)
app.include_router(estadisticas.router)
app.include_router(mapa.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "EcoReport API"}


@app.get("/api/diag")
def diag():
    import sys, importlib
    info = {
        "python": sys.version,
        "platform": sys.platform,
        "db_server": os.getenv("DB_SERVER", "no-set"),
        "db_name": os.getenv("DB_NAME", "no-set"),
        "db_user": os.getenv("DB_USER", "no-set"),
        "cors_origins": os.getenv("CORS_ORIGINS", "no-set"),
    }
    try:
        import pymssql
        info["pymssql"] = pymssql.__version__
    except Exception as e:
        info["pymssql"] = f"error: {e}"
    try:
        import pyodbc
        info["pyodbc"] = pyodbc.version
    except Exception as e:
        info["pyodbc"] = f"error: {e}"
    try:
        from .config import CONNECTION_STRING
        info["connection_string_prefix"] = CONNECTION_STRING[:60]
    except Exception as e:
        info["config_error"] = str(e)
    return info
