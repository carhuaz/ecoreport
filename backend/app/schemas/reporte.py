from pydantic import BaseModel
from typing import Optional


class ReporteCreate(BaseModel):
    titulo: str
    descripcion: str
    distrito: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    imagenes: Optional[list[str]] = None
    prioridad: Optional[str] = 'Media'
    puntaje_prioridad: Optional[int] = 0
    criterios_prioridad: Optional[list[str]] = None
    anonimo: Optional[bool] = False


class ReporteUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    distrito: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class PrioridadRequest(BaseModel):
    prioridad: str
    observacion: str


class AsignarCuadrillaRequest(BaseModel):
    cuadrilla_id: int


class ValidacionRequest(BaseModel):
    observacion: str
