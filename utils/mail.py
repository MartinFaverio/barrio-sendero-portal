import smtplib
from email.mime.text import MIMEText
from os import getenv

EMAIL_USER = getenv("EMAIL_USER")
EMAIL_PASS = getenv("EMAIL_PASS")

def enviar_mail_confirmacion(destinatario, link):
    asunto = "Confirmá tu registro en Barrio Sendero"
    cuerpo = f"""
    Hola! Gracias por registrarte en el portal Barrio Sendero.
    Para confirmar tu cuenta, hacé clic en el siguiente enlace:

    {link}

    Si no te registraste, ignorá este mensaje.
    """

    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = EMAIL_USER
    msg['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)