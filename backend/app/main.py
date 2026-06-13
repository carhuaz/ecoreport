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
    import sys, os
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
        info["pymssql_version"] = pymssql.__version__
        conn = pymssql.connect(
            server=os.environ["DB_SERVER"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            tds_version="7.4",
            timeout=10,
            login_timeout=10
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS test")
        row = cursor.fetchone()
        info["db_test"] = f"OK - {row[0]}"
        conn.close()
    except Exception as e:
        info["db_error"] = repr(e)
    try:
        import pymssql
        info["pymssql_paramstyle"] = pymssql.paramstyle
        conn2 = pymssql.connect(
            server=os.environ["DB_SERVER"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            tds_version="7.4",
            timeout=10,
            login_timeout=10
        )
        cursor = conn2.cursor()
        cursor.execute("SELECT id, nombre, email FROM usuarios WHERE email = %s", ("admin@ecoreport.pe",))
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        info["db_query_test"] = dict(zip(cols, row)) if row else "no rows"
        conn2.close()
    except Exception as e:
        info["db_query_error"] = repr(e)
    return info
