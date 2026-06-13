def test_imports():
    from app.config import SECRET_KEY, ALGORITHM, DB_SERVER
    from app.middleware.auth import hash_password, verify_password, create_access_token
    from app.email_service import generar_otp, _construir_html
    assert SECRET_KEY is not None
    assert ALGORITHM == "HS256"
    otp = generar_otp()
    assert len(otp) == 6
    assert otp.isdigit()
    html = _construir_html("Test", "123456")
    assert "Test" in html
    assert "123456" in html
