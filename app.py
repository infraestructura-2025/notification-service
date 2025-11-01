from flask import Flask, request, jsonify
import os
import logging
import threading
import traceback

# Opcionales según el modo (SES)
try:
    import boto3
except Exception:
    boto3 = None

import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración vía env vars (defaults para desarrollo)
USE_SES = os.environ.get("USE_SES", "false").lower() == "true"
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "castromoraleslab@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "dphlnjgpfarunmwd")
SES_REGION = os.environ.get("SES_REGION", "us-east-1")
SES_SOURCE_EMAIL = os.environ.get("SES_SOURCE_EMAIL", "castromoraleslab@gmail.com")
SES_DEST_EMAIL = os.environ.get("SES_DEST_EMAIL", SES_SOURCE_EMAIL)
SEND_SYNC = os.environ.get("SEND_SYNC", "false").lower() == "true"  # si true, enviar de forma sincrónica (útil para debug)

def send_via_smtp(user_data):
    """Envía email vía SMTP (Gmail u otro proveedor)."""
    try:
        subject = "Nuevo usuario creado"
        body = f"""
Se ha registrado un nuevo usuario en el sistema:

• Nombre: {user_data.get('name')}
• Email: {user_data.get('email')}
• Teléfono: {user_data.get('phone')}
• Fecha: {user_data.get('created_at', 'N/A')}
"""
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = SES_DEST_EMAIL or SMTP_USER

        logger.info("Conectando a servidor SMTP %s:%s", SMTP_HOST, SMTP_PORT)
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.ehlo()
        if SMTP_PORT in (587, 25):
            server.starttls()
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        logger.info("Email enviado vía SMTP a %s", msg['To'])
        return True, None
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Error enviando vía SMTP: %s\n%s", str(e), tb)
        return False, str(e)

def send_via_ses(user_data):
    """Envía email usando AWS SES (boto3)."""
    if boto3 is None:
        msg = "boto3 no está instalado"
        logger.error(msg)
        return False, msg

    try:
        client = boto3.client('ses', region_name=SES_REGION)
        subject = "Nuevo usuario creado"
        body = f"""
Se ha registrado un nuevo usuario en el sistema:

• Nombre: {user_data.get('name')}
• Email: {user_data.get('email')}
• Teléfono: {user_data.get('phone')}
• Fecha: {user_data.get('created_at', 'N/A')}
"""
        resp = client.send_email(
            Source=SES_SOURCE_EMAIL,
            Destination={'ToAddresses': [SES_DEST_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        logger.info("Email enviado vía SES: MessageId=%s", resp.get('MessageId'))
        return True, None
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Error enviando vía SES: %s\n%s", str(e), tb)
        return False, str(e)

def worker_send_email(user_data):
    """Thread worker: decide el método y envía el email."""
    try:
        if USE_SES:
            ok, err = send_via_ses(user_data)
        else:
            ok, err = send_via_smtp(user_data)
        if not ok:
            logger.warning("Fallo en envío de notificación: %s", err)
    except Exception as e:
        logger.error("Excepción en worker_send_email: %s\n%s", e, traceback.format_exc())

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "notification-service"})

@app.route('/notify', methods=['POST'])
def notify():
    """
    Recibe POST /notify con JSON del usuario y dispara email (async por defecto).
    """
    try:
        logger.info("Solicitud de notificación recibida")
        data = request.get_json()
        if not data:
            logger.warning("No JSON recibido")
            return jsonify({"error": "No JSON data provided"}), 400

        # Validaciones mínimas
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        if not name or not email:
            return jsonify({"error": "Campos 'name' y 'email' son requeridos"}), 400

        # Si SEND_SYNC true, enviar sin hilo (útil para debug)
        if SEND_SYNC:
            logger.info("SEND_SYNC=true -> envío sincrónico")
            if USE_SES:
                ok, err = send_via_ses(data)
            else:
                ok, err = send_via_smtp(data)
            if not ok:
                return jsonify({"error": "Error enviando notificación", "detail": err}), 500
            return jsonify({"status": "success", "message": "Notificación enviada"}), 200

        # Envío no bloqueante en otro hilo
        thread = threading.Thread(target=worker_send_email, args=(data,))
        thread.daemon = True
        thread.start()

        logger.info("Notificación encolada para %s (%s)", name, email)
        return jsonify({"status": "accepted", "message": "Notificación en proceso", "user": name}), 202

    except Exception as e:
        logger.error("Error en /notify: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

