from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from ..database import fetch_all, fetch_one, execute, execute_returning_id
from ..schemas.reporte import ReporteCreate, ReporteUpdate, PrioridadRequest, AsignarCuadrillaRequest, ValidacionRequest
from ..middleware.auth import get_current_user_id, get_current_user_role, require_roles
import json

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


def _serializar_reporte(row: dict) -> dict:
    if row.get("criterios_prioridad") and isinstance(row["criterios_prioridad"], str):
        row["criterios_prioridad"] = json.loads(row["criterios_prioridad"])
    if row.get("imagenes") and isinstance(row["imagenes"], str):
        row["imagenes"] = json.loads(row["imagenes"])
    if row.get("fecha") and hasattr(row["fecha"], 'strftime'):
        row["fecha"] = row["fecha"].strftime("%Y-%m-%d")
    if row.get("anonimo"):
        row["ciudadano_nombre"] = "Anónimo"
    return row


def _adjuntar_historial(reportes: list[dict]) -> list[dict]:
    for r in reportes:
        historial = fetch_all(
            "SELECT id, FORMAT(fecha, 'yyyy-MM-dd') as fecha, accion, usuario, observacion FROM historial_reportes WHERE reporte_id = ? ORDER BY fecha ASC",
            (r["id"],)
        )
        r["historial"] = historial
    return reportes


def _paginar(sql_count: str, sql_data: str, params: list, page: int, page_size: int) -> dict:
    total = fetch_one(sql_count, tuple(params))["total"]
    offset = (page - 1) * page_size
    sql_paginado = f"{sql_data} OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
    rows = fetch_all(sql_paginado, tuple(params))
    return {
        "items": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size)
    }


@router.get("")
def listar_reportes(
    estado: Optional[str] = None,
    distrito: Optional[str] = None,
    prioridad: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user_role)
):
    where = "WHERE 1=1"
    params: list = []
    if estado:
        where += " AND r.estado = ?"
        params.append(estado)
    if distrito:
        where += " AND r.distrito = ?"
        params.append(distrito)
    if prioridad:
        where += " AND r.prioridad = ?"
        params.append(prioridad)

    count_sql = f"SELECT COUNT(*) as total FROM reportes r {where}"
    data_sql = f"""
        SELECT r.*, u.nombre as ciudadano_nombre,
               FORMAT(r.fecha, 'yyyy-MM-dd') as fecha
        FROM reportes r
        LEFT JOIN usuarios u ON r.ciudadano_id = u.id
        {where}
        ORDER BY r.fecha DESC
    """

    result = _paginar(count_sql, data_sql, params, page, page_size)
    result["items"] = _adjuntar_historial([_serializar_reporte(r) for r in result["items"]])
    return result


@router.get("/publicos")
def listar_reportes_publicos(
    distrito: Optional[str] = None,
    estado: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    where = "WHERE r.estado NOT IN ('Pendiente', 'Rechazado')"
    params: list = []
    if distrito:
        where += " AND r.distrito = ?"
        params.append(distrito)
    if estado:
        where += " AND r.estado = ?"
        params.append(estado)

    count_sql = f"SELECT COUNT(*) as total FROM reportes r {where}"
    data_sql = f"""
        SELECT r.*, u.nombre as ciudadano_nombre,
               FORMAT(r.fecha, 'yyyy-MM-dd') as fecha
        FROM reportes r
        LEFT JOIN usuarios u ON r.ciudadano_id = u.id
        {where}
        ORDER BY r.fecha DESC
    """

    result = _paginar(count_sql, data_sql, params, page, page_size)
    result["items"] = _adjuntar_historial([_serializar_reporte(r) for r in result["items"]])
    return result


@router.get("/mis-reportes")
def mis_reportes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id)
):
    where = "WHERE r.ciudadano_id = ?"
    params = [user_id]

    count_sql = f"SELECT COUNT(*) as total FROM reportes r {where}"
    data_sql = f"""
        SELECT r.*, u.nombre as ciudadano_nombre,
               FORMAT(r.fecha, 'yyyy-MM-dd') as fecha
        FROM reportes r
        LEFT JOIN usuarios u ON r.ciudadano_id = u.id
        {where}
        ORDER BY r.fecha DESC
    """

    result = _paginar(count_sql, data_sql, params, page, page_size)
    result["items"] = _adjuntar_historial([_serializar_reporte(r) for r in result["items"]])
    return result


@router.get("/{reporte_id}")
def obtener_reporte(reporte_id: int):
    row = fetch_one("""
        SELECT r.*, u.nombre as ciudadano_nombre,
               FORMAT(r.fecha, 'yyyy-MM-dd') as fecha
        FROM reportes r
        LEFT JOIN usuarios u ON r.ciudadano_id = u.id
        WHERE r.id = ?
    """, (reporte_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    row = _serializar_reporte(row)

    historial = fetch_all(
        "SELECT id, FORMAT(fecha, 'yyyy-MM-dd') as fecha, accion, usuario, observacion FROM historial_reportes WHERE reporte_id = ? ORDER BY fecha ASC",
        (reporte_id,)
    )
    row["historial"] = historial
    return row


@router.post("")
def crear_reporte(req: ReporteCreate, user_id: int = Depends(get_current_user_id)):
    imagenes_json = json.dumps(req.imagenes or [], ensure_ascii=False)
    criterios_json = json.dumps(req.criterios_prioridad or [], ensure_ascii=False) if hasattr(req, 'criterios_prioridad') else '[]'

    ciudadano_id_val = None if req.anonimo else user_id
    nombre_usuario = "Anónimo" if req.anonimo else (fetch_one("SELECT nombre FROM usuarios WHERE id = ?", (user_id,)) or {}).get("nombre", "Ciudadano")

    reporte_id = execute_returning_id(
        """INSERT INTO reportes (titulo, descripcion, distrito, direccion, latitud, longitud, imagenes, ciudadano_id, prioridad, puntaje_prioridad, criterios_prioridad, anonimo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (req.titulo, req.descripcion, req.distrito, req.direccion, req.latitud, req.longitud, imagenes_json, ciudadano_id_val,
         req.prioridad or 'Media', req.puntaje_prioridad or 0, criterios_json, 1 if req.anonimo else 0)
    )

    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario) VALUES (?, 'Reporte creado', ?)",
        (reporte_id, nombre_usuario)
    )

    return {"mensaje": "Reporte creado exitosamente", "id": reporte_id}


@router.put("/{reporte_id}")
def actualizar_reporte(reporte_id: int, req: ReporteUpdate, user_id: int = Depends(get_current_user_id)):
    reporte = fetch_one("SELECT id, ciudadano_id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if reporte["ciudadano_id"] != user_id:
        raise HTTPException(status_code=403, detail="No puedes editar este reporte")

    updates = {}
    for field in ("titulo", "descripcion", "distrito", "direccion", "latitud", "longitud"):
        val = getattr(req, field, None)
        if val is not None:
            updates[field] = val

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [reporte_id]
        execute(f"UPDATE reportes SET {set_clause} WHERE id = ?", tuple(params))

    return {"mensaje": "Reporte actualizado"}


@router.delete("/{reporte_id}")
def eliminar_reporte(reporte_id: int, user=Depends(require_roles("Administrador"))):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("DELETE FROM historial_reportes WHERE reporte_id = ?", (reporte_id,))
    execute("DELETE FROM reportes WHERE id = ?", (reporte_id,))
    return {"mensaje": "Reporte eliminado"}


# --- Transiciones de estado ---

@router.post("/{reporte_id}/aprobar")
def aprobar_reporte(reporte_id: int, req: ValidacionRequest, user=Depends(require_roles("Validador", "Administrador"))):
    reporte = fetch_one("SELECT id, estado FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("UPDATE reportes SET estado = 'Aprobado' WHERE id = ?", (reporte_id,))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario, observacion) VALUES (?, 'Aprobado', ?, ?)",
        (reporte_id, user["id"], req.observacion)
    )
    return {"mensaje": "Reporte aprobado"}


@router.post("/{reporte_id}/rechazar")
def rechazar_reporte(reporte_id: int, req: ValidacionRequest, user=Depends(require_roles("Validador", "Administrador"))):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("UPDATE reportes SET estado = 'Rechazado', observacion_validacion = ? WHERE id = ?",
            (req.observacion, reporte_id))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario, observacion) VALUES (?, 'Rechazado', ?, ?)",
        (reporte_id, user["id"], req.observacion)
    )
    return {"mensaje": "Reporte rechazado"}


@router.post("/{reporte_id}/corregir-prioridad")
def corregir_prioridad(reporte_id: int, req: PrioridadRequest, user=Depends(require_roles("Validador", "Administrador"))):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute(
        "UPDATE reportes SET prioridad = ?, prioridad_corregida = 1, observacion_prioridad = ? WHERE id = ?",
        (req.prioridad, req.observacion, reporte_id)
    )
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario, observacion) VALUES (?, 'Prioridad corregida', ?, ?)",
        (reporte_id, user["id"], req.observacion)
    )
    return {"mensaje": "Prioridad corregida"}


@router.post("/{reporte_id}/asignar-cuadrilla")
def asignar_cuadrilla(reporte_id: int, req: AsignarCuadrillaRequest, user=Depends(require_roles("Administrador"))):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    cuadrilla = fetch_one("SELECT id, nombre FROM cuadrillas WHERE id = ?", (req.cuadrilla_id,))
    if not cuadrilla:
        raise HTTPException(status_code=404, detail="Cuadrilla no encontrada")

    execute("UPDATE reportes SET estado = 'Programado', cuadrilla_id = ? WHERE id = ?",
            (req.cuadrilla_id, reporte_id))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario, observacion) VALUES (?, 'Asignado a cuadrilla', ?, ?)",
        (reporte_id, "Admin", f"Asignado a {cuadrilla['nombre']}")
    )
    return {"mensaje": f"Reporte asignado a {cuadrilla['nombre']}"}


@router.post("/{reporte_id}/atender")
def marcar_en_atencion(reporte_id: int, user=Depends(get_current_user_role)):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("UPDATE reportes SET estado = 'En atención' WHERE id = ?", (reporte_id,))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario) VALUES (?, 'En atención', ?)",
        (reporte_id, f"User {user['id']}")
    )
    return {"mensaje": "Reporte en atención"}


@router.post("/{reporte_id}/completar")
def marcar_atendido(reporte_id: int, user=Depends(get_current_user_role)):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("UPDATE reportes SET estado = 'Atendido' WHERE id = ?", (reporte_id,))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario) VALUES (?, 'Atendido', ?)",
        (reporte_id, f"User {user['id']}")
    )
    return {"mensaje": "Reporte marcado como atendido"}


@router.post("/{reporte_id}/verificar")
def marcar_verificado(reporte_id: int, user=Depends(require_roles("Administrador"))):
    reporte = fetch_one("SELECT id FROM reportes WHERE id = ?", (reporte_id,))
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    execute("UPDATE reportes SET estado = 'Verificado' WHERE id = ?", (reporte_id,))
    execute(
        "INSERT INTO historial_reportes (reporte_id, accion, usuario) VALUES (?, 'Verificado', ?)",
        (reporte_id, f"User {user['id']}")
    )
    return {"mensaje": "Reporte verificado"}


@router.post("/{reporte_id}/calcular-prioridad")
def calcular_prioridad(reporte_id: int, respuestas: dict, user=Depends(get_current_user_role)):
    puntaje = 0
    criterios = []

    cantidad = respuestas.get("cantidad", 0)
    if cantidad == 1:
        puntaje += 1
        criterios.append("Poca basura")
    elif cantidad == 2:
        puntaje += 2
        criterios.append("Varias bolsas acumuladas")
    elif cantidad == 3:
        puntaje += 3
        criterios.append("Gran acumulación de basura o desmonte")

    if respuestas.get("malosOlores"):
        puntaje += 2
        criterios.append("Malos olores")
    if respuestas.get("animales"):
        puntaje += 3
        criterios.append("Presencia de animales, insectos o roedores")
    if respuestas.get("cercania"):
        puntaje += 3
        criterios.append("Cercanía a viviendas, colegios, mercados, restaurantes o zonas concurridas")
    if respuestas.get("agua"):
        puntaje += 3
        criterios.append("Cercanía a río, canal, acequia o área verde")
    if respuestas.get("bloqueo"):
        puntaje += 3
        criterios.append("Bloqueo de vereda, pista o zona de tránsito")
    if respuestas.get("peligroso"):
        puntaje += 4
        criterios.append("Residuos peligrosos o sospechosos")
    if respuestas.get("imagenClara"):
        puntaje += 1
        criterios.append("Imagen clara como evidencia")

    if puntaje >= 12:
        prioridad = "Crítica"
    elif puntaje >= 8:
        prioridad = "Alta"
    elif puntaje >= 4:
        prioridad = "Media"
    else:
        prioridad = "Baja"

    execute(
        "UPDATE reportes SET prioridad = ?, puntaje_prioridad = ?, criterios_prioridad = ? WHERE id = ?",
        (prioridad, puntaje, json.dumps(criterios, ensure_ascii=False), reporte_id)
    )

    return {"prioridad": prioridad, "puntaje": puntaje, "criterios": criterios}
