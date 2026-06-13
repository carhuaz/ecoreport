import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, VerifyRequest
from app.schemas.reporte import ReporteCreate, ReporteUpdate, PrioridadRequest, AsignarCuadrillaRequest, ValidacionRequest
from app.schemas.usuario import CambiarRolRequest


def test_login_request():
    req = LoginRequest(email="test@test.com", password="123456")
    assert req.email == "test@test.com"
    assert req.password == "123456"


def test_register_request():
    req = RegisterRequest(nombre="Juan", email="juan@test.com", password="abc123", dni="12345678")
    assert req.dni == "12345678"
    assert req.email == "juan@test.com"


def test_auth_response():
    resp = AuthResponse(id=1, nombre="Juan", email="j@test.com", rol="Ciudadano", activo=True, token="abc.def.ghi")
    assert resp.id == 1
    assert resp.rol == "Ciudadano"
    assert resp.activo is True


def test_reporte_create_defaults():
    req = ReporteCreate(titulo="Test", descripcion="Desc", distrito="Huancayo", direccion="Av. Principal")
    assert req.prioridad == "Media"
    assert req.puntaje_prioridad == 0
    assert req.anonimo is False
    assert req.imagenes is None


def test_reporte_create_con_anonimo():
    req = ReporteCreate(titulo="T", descripcion="D", distrito="H", direccion="Av.", anonimo=True)
    assert req.anonimo is True


def test_cambiar_rol_request():
    req = CambiarRolRequest(rol="Validador")
    assert req.rol == "Validador"


def test_validacion_request():
    req = ValidacionRequest(observacion="Se aprobó el reporte")
    assert req.observacion == "Se aprobó el reporte"
