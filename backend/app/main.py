from fastapi import FastAPI

from .routes import auth, reportes, usuarios, cuadrillas, estadisticas, mapa

app = FastAPI(
    title="EcoReport API",
    description="API REST para el sistema de reportes ambientales",
    version="1.0.0"
)

# CORS manejado por Azure App Service (API > CORS)
# Para desarrollo local, usar proxy o extensión de navegador

app.include_router(auth.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)
app.include_router(cuadrillas.router)
app.include_router(estadisticas.router)
app.include_router(mapa.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "EcoReport API"}
