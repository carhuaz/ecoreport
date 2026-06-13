import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.middleware.auth import hash_password, verify_password, create_access_token
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM


def test_hash_y_verificacion():
    password = "MiPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("OtraPassword", hashed)


def test_token_creacion_y_decode():
    data = {"id": 1, "rol": "Ciudadano"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["id"] == 1
    assert payload["rol"] == "Ciudadano"
    assert "exp" in payload


def test_token_con_datos_multiples():
    data = {"id": 42, "rol": "Administrador", "extra": "test"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["id"] == 42
    assert payload["rol"] == "Administrador"
    assert payload["extra"] == "test"
