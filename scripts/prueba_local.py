"""
Prueba rápida contra la API local.
Ejemplo: python scripts/prueba_local.py
"""
import httpx
import sys
import os
import random

BASE = "http://localhost:8000"
EMAIL = f"test_{os.urandom(4).hex()}@prueba.pe"
PASSWORD = "Test123456"
DNI = str(random.randint(10000000, 99999999))

client = httpx.Client(base_url=BASE, timeout=15)

ok = 0
fail = 0

def test(nombre, metodo, ruta, **kwargs):
    global ok, fail
    try:
        r = getattr(client, metodo)(ruta, **kwargs)
        print(f"  {'✅' if r.is_success else '❌'} {r.status_code} {metodo.upper()} {ruta}  →  {nombre}")
        if r.is_success:
            ok += 1
        else:
            print(f"       {r.text[:200]}")
            fail += 1
        return r
    except Exception as e:
        print(f"  ❌ ERROR {metodo.upper()} {ruta}  →  {nombre}: {e}")
        fail += 1
        return None

print("=" * 60)
print("  EcoReport - Prueba de humo")
print("=" * 60)

# 1. Health
print("\n📡 Health")
test("health", "get", "/api/health")

# 2. Registro
print("\n📝 Registro")
r = test("registrar usuario", "post", "/api/auth/register", json={
    "nombre": "Usuario Prueba",
    "email": EMAIL,
    "password": PASSWORD,
    "dni": DNI,
})

# 3. Login
print("\n🔑 Login")
r = test("iniciar sesión", "post", "/api/auth/login", json={
    "email": "admin@ecoreport.pe",
    "password": "123456",
})
token = r.json().get("token", "") if r and r.is_success else ""
headers = {"Authorization": f"Bearer {token}"}

if token:
    # 4. /me
    print("\n👤 Perfil")
    test("obtener perfil", "get", "/api/auth/me", headers=headers)

    # 5. Reportes públicos
    print("\n📋 Reportes públicos")
    test("listar públicos", "get", "/api/reportes/publicos")

    # 6. Estadísticas
    print("\n📊 Estadísticas")
    test("resumen", "get", "/api/estadisticas/resumen", headers=headers)
    test("por estado", "get", "/api/estadisticas/por-estado", headers=headers)
    test("por distrito", "get", "/api/estadisticas/por-distrito", headers=headers)
    test("por prioridad", "get", "/api/estadisticas/por-prioridad", headers=headers)
    test("cuadrillas resumen", "get", "/api/estadisticas/cuadrillas-resumen", headers=headers)

    # 7. Mapa
    print("\n🗺️  Mapa")
    test("reportes en mapa", "get", "/api/mapa/reportes", headers=headers)

    # 8. Cuadrillas
    print("\n👷 Cuadrillas")
    test("listar cuadrillas", "get", "/api/cuadrillas", headers=headers)
    test("cuadrillas disponibles", "get", "/api/cuadrillas/disponibles", headers=headers)

else:
    print("  ⚠️  Sin token - se saltan rutas protegidas")

print("\n" + "=" * 60)
print(f"  Resultado: {ok} ✅  |  {fail} ❌")
print("=" * 60)
sys.exit(0 if fail == 0 else 1)
