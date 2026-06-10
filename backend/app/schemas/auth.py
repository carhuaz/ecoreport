from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    nombre: str
    email: str
    password: str
    dni: str


class AuthResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    token: str


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_registro: str


class VerifyRequest(BaseModel):
    email: str
    codigo: str
