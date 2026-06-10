from fastapi import APIRouter, Depends
from ..database import fetch_all
from ..middleware.auth import get_current_user_role

router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])


@router.get("/resumen")
def resumen(user=Depends(get_current_user_role)):
    total = fetch_all("SELECT COUNT(*) as total FROM reportes")[0]["total"]
    por_estado = fetch_all("SELECT estado, COUNT(*) as cantidad FROM reportes GROUP BY estado")
    por_distrito = fetch_all("SELECT distrito, COUNT(*) as cantidad FROM reportes GROUP BY distrito")
    por_prioridad = fetch_all("SELECT prioridad, COUNT(*) as cantidad FROM reportes GROUP BY prioridad")

    return {
        "total_reportes": total,
        "por_estado": por_estado,
        "por_distrito": por_distrito,
        "por_prioridad": por_prioridad
    }


@router.get("/por-estado")
def por_estado(user=Depends(get_current_user_role)):
    return fetch_all("SELECT estado, COUNT(*) as cantidad FROM reportes GROUP BY estado ORDER BY estado")


@router.get("/por-distrito")
def por_distrito(user=Depends(get_current_user_role)):
    return fetch_all("SELECT distrito, COUNT(*) as cantidad FROM reportes GROUP BY distrito ORDER BY distrito")


@router.get("/por-prioridad")
def por_prioridad(user=Depends(get_current_user_role)):
    return fetch_all("SELECT prioridad, COUNT(*) as cantidad FROM reportes GROUP BY prioridad ORDER BY prioridad")


@router.get("/cuadrillas-resumen")
def cuadrillas_resumen(user=Depends(get_current_user_role)):
    return fetch_all("""
        SELECT c.id, c.nombre, c.estado, c.distrito,
               COUNT(r.id) as reportes_activos
        FROM cuadrillas c
        LEFT JOIN reportes r ON c.id = r.cuadrilla_id AND r.estado IN ('Programado', 'En atención')
        GROUP BY c.id, c.nombre, c.estado, c.distrito
        ORDER BY c.id
    """)
