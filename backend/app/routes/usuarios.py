from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..database import fetch_all, fetch_one, execute
from ..schemas.usuario import CambiarRolRequest
from ..middleware.auth import require_roles

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("")
def listar_usuarios(termino: Optional[str] = None, rol: Optional[str] = None,
                    user=Depends(require_roles("Administrador"))):
    sql = """
        SELECT id, nombre, email, dni, rol, activo,
               FORMAT(fecha_registro, 'yyyy-MM-dd') as fecha_registro
        FROM usuarios WHERE 1=1
    """
    params = []
    if termino:
        sql += " AND (LOWER(nombre) LIKE ? OR LOWER(email) LIKE ?)"
        params.extend([f"%{termino.lower()}%", f"%{termino.lower()}%"])
    if rol:
        sql += " AND rol = ?"
        params.append(rol)
    sql += " ORDER BY id"

    return fetch_all(sql, tuple(params))


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, user=Depends(require_roles("Administrador"))):
    user = fetch_one(
        "SELECT id, nombre, email, dni, rol, activo, FORMAT(fecha_registro, 'yyyy-MM-dd') as fecha_registro FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{usuario_id}/rol")
def cambiar_rol(usuario_id: int, req: CambiarRolRequest, user=Depends(require_roles("Administrador"))):
    if req.rol not in ("Ciudadano", "Validador", "Administrador"):
        raise HTTPException(status_code=400, detail="Rol inválido")
    usuario = fetch_one("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    execute("UPDATE usuarios SET rol = ? WHERE id = ?", (req.rol, usuario_id))
    return {"mensaje": "Rol actualizado"}


@router.put("/{usuario_id}/activar")
def activar_usuario(usuario_id: int, user=Depends(require_roles("Administrador"))):
    usuario = fetch_one("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    execute("UPDATE usuarios SET activo = 1 WHERE id = ?", (usuario_id,))
    return {"mensaje": "Usuario activado"}


@router.put("/{usuario_id}/desactivar")
def desactivar_usuario(usuario_id: int, user=Depends(require_roles("Administrador"))):
    usuario = fetch_one("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario_id == user["id"]:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")
    execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
    return {"mensaje": "Usuario desactivado"}
