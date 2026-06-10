from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..database import fetch_all, fetch_one, execute
from ..middleware.auth import require_roles, get_current_user_role


class CuadrillaCreate(BaseModel):
    nombre: str
    responsable: str
    distrito: str
    zona_asignada: Optional[str] = None


class CuadrillaUpdate(BaseModel):
    nombre: Optional[str] = None
    responsable: Optional[str] = None
    distrito: Optional[str] = None
    zona_asignada: Optional[str] = None
    estado: Optional[str] = None


router = APIRouter(prefix="/api/cuadrillas", tags=["Cuadrillas"])


def _serializar(row: dict) -> dict:
    if not row:
        return row
    return {
        "id": row["id"],
        "nombre": row["nombre"],
        "responsable": row["responsable"],
        "estado": row["estado"],
        "zonaAsignada": row.get("zona_asignada"),
        "distrito": row["distrito"]
    }


@router.get("")
def listar_cuadrillas(user=Depends(get_current_user_role)):
    rows = fetch_all("SELECT * FROM cuadrillas ORDER BY id")
    return [_serializar(r) for r in rows]


@router.get("/disponibles")
def cuadrillas_disponibles(user=Depends(get_current_user_role)):
    rows = fetch_all("SELECT * FROM cuadrillas WHERE estado = 'Disponible' ORDER BY id")
    return [_serializar(r) for r in rows]


@router.get("/{cuadrilla_id}")
def obtener_cuadrilla(cuadrilla_id: int, user=Depends(get_current_user_role)):
    cuadrilla = fetch_one("SELECT * FROM cuadrillas WHERE id = ?", (cuadrilla_id,))
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")
    return _serializar(cuadrilla)


@router.post("")
def crear_cuadrilla(req: CuadrillaCreate, user=Depends(require_roles("Administrador"))):
    if not req.nombre or not req.responsable or not req.distrito:
        raise HTTPException(status_code=400, detail="Nombre, responsable y distrito son obligatorios")
    execute(
        "INSERT INTO cuadrillas (nombre, responsable, distrito, zona_asignada) VALUES (?, ?, ?, ?)",
        (req.nombre, req.responsable, req.distrito, req.zona_asignada or '')
    )
    return {"mensaje": "Cuadrilla creada exitosamente"}


@router.put("/{cuadrilla_id}")
def actualizar_cuadrilla(cuadrilla_id: int, req: CuadrillaUpdate, user=Depends(require_roles("Administrador"))):
    cuadrilla = fetch_one("SELECT id FROM cuadrillas WHERE id = ?", (cuadrilla_id,))
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")

    updates = {}
    for field in ("nombre", "responsable", "distrito", "zona_asignada", "estado"):
        val = getattr(req, field, None)
        if val is not None:
            updates[field] = val

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [cuadrilla_id]
        execute(f"UPDATE cuadrillas SET {set_clause} WHERE id = ?", tuple(params))

    return {"mensaje": "Cuadrilla actualizada"}


@router.delete("/{cuadrilla_id}")
def eliminar_cuadrilla(cuadrilla_id: int, user=Depends(require_roles("Administrador"))):
    cuadrilla = fetch_one("SELECT id FROM cuadrillas WHERE id = ?", (cuadrilla_id,))
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")

    reportes_asignados = fetch_one(
        "SELECT COUNT(*) as total FROM reportes WHERE cuadrilla_id = ? AND estado NOT IN ('Atendido', 'Verificado')",
        (cuadrilla_id,)
    )
    if reportes_asignados and reportes_asignados["total"] > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: la cuadrilla tiene reportes activos asignados")

    execute("UPDATE reportes SET cuadrilla_id = NULL WHERE cuadrilla_id = ?", (cuadrilla_id,))
    execute("DELETE FROM cuadrillas WHERE id = ?", (cuadrilla_id,))
    return {"mensaje": "Cuadrilla eliminada"}


@router.post("/{cuadrilla_id}/asignar-revision")
def asignar_a_cuadrilla(cuadrilla_id: int, reporte_id: int, user=Depends(require_roles("Administrador"))):
    cuadrilla = fetch_one("SELECT id, nombre FROM cuadrillas WHERE id = ?", (cuadrilla_id,))
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")

    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    execute("UPDATE reportes SET estado = 'Programado', cuadrilla_id = ? WHERE id = ?",
            (cuadrilla_id, reporte_id))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario, observacion) VALUES (?, 'Asignado a cuadrilla', ?, ?)",
        (reporte_id, "Admin", f"Asignado a {cuadrilla['nombre']}")
    )

    if cuadrilla["estado"] == "Disponible":
        execute("UPDATE cuadrillas SET estado = 'En ruta' WHERE id = ?", (cuadrilla_id,))

    return {"mensaje": f"Reporte asignado a {cuadrilla['nombre']}"}
