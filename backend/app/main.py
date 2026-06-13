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
        "env_ok": {k: os.getenv(k) for k in ["DB_SERVER", "DB_NAME", "DB_USER"]},
        "cors_origins": os.getenv("CORS_ORIGINS", "no-set"),
    }
    info["db_has_password"] = "yes" if os.getenv("DB_PASSWORD") else "no"
    try:
        from .database import fetch_one
        row = fetch_one("SELECT id, nombre, email FROM usuarios WHERE email = ?", ("admin@ecoreport.pe",))
        info["fetch_one_test"] = row
    except Exception as e:
        info["fetch_one_error"] = repr(e)
    try:
        from .database import fetch_all
        rows = fetch_all("SELECT id, nombre, email FROM usuarios")
        info["fetch_all_test"] = f"{len(rows)} usuarios"
    except Exception as e:
        info["fetch_all_error"] = repr(e)
    try:
        from .middleware.auth import hash_password, verify_password, create_access_token
        from .schemas.auth import AuthResponse
        hashed = hash_password("123456")
        info["bcrypt_test"] = verify_password("123456", hashed)
        token = create_access_token({"id": 1, "rol": "Admin"})
        info["jwt_test"] = f"token_ok:{len(token)}"
        resp = AuthResponse(id=1, nombre="Test", email="t@t.com", rol="Admin", activo=True, token=token)
        info["pydantic_test"] = resp.model_dump()["rol"]
    except Exception as e:
        info["auth_error"] = repr(e)
    try:
        from .routes.auth import login
        info["import_login"] = "ok"
    except Exception as e:
        info["import_login_error"] = repr(e)
    return info
