import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


def generar_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def _construir_html(nombre: str, codigo: str) -> str:
    # 1. Se añadió lang="es" a la etiqueta <html>
    # 2. Se forzó Arial/sans-serif en el código para que no parezca sintaxis de programación externa
    return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Verificación de Cuenta EcoReport</title>
</head>
<body style="margin:0;padding:0;background:#f4f7f5;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
          <tr>
            <td style="background:#16803c;padding:32px;text-align:center;">
              <span style="font-size:40px;">🌿</span>
              <h1 style="color:#fff;margin:8px 0 0;font-size:22px;">EcoReport Huancayo</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <h2 style="color:#1f2937;font-size:18px;margin:0 0 8px;">Hola, <strong>{nombre}</strong></h2>
              <p style="color:#6b7280;font-size:14px;line-height:1.6;margin:0 0 20px;">
                Gracias por registrarte. Para completar tu registro y activar tu cuenta ciudadana,
                por favor ingresa el siguiente código de verificación en nuestra plataforma:
              </p>
              <div style="text-align:center;margin:24px 0;">
                <span style="display:inline-block;background:#f3f4f6;border-radius:12px;padding:16px 32px;font-size:36px;font-weight:800;letter-spacing:8px;color:#16803c;font-family:Arial,sans-serif;">{codigo}</span>
              </div>
              <p style="color:#9ca3af;font-size:12px;line-height:1.5;">
                Este código de seguridad expira en 10 minutos. Si tú no solicitaste este registro, puedes ignorar este mensaje de manera segura.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#f9fafb;padding:16px 32px;text-align:center;">
              <span style="color:#9ca3af;font-size:11px;">
                EcoReport – Plataforma ciudadana de reportes ambientales<br>
                Municipalidad Provincial de Huancayo
              </span>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _enviar(destinatario: str, asunto: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    
    # 3. Se añaden encabezados explícitos de idioma y codificación al correo
    msg["Content-Language"] = "es"
    
    # 4. Aseguramos que el MIMEText use codificación utf-8 explícita
    html_part = MIMEText(html, "html", "utf-8")
    msg.attach(html_part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def enviar_otp_background(nombre: str, destinatario: str, codigo: str) -> None:
    """Wrapper para BackgroundTasks – recibe solo args serializables."""
    try:
        _enviar(destinatario, "EcoReport – Verifica tu cuenta", _construir_html(nombre, codigo))
    except Exception as exc:
        print(f"[email_service] Error enviando OTP a {destinatario}: {exc}")


def disparar_verificacion(background_tasks: BackgroundTasks, nombre: str, email: str, codigo: str) -> None:
    background_tasks.add_task(enviar_otp_background, nombre, email, codigo)
