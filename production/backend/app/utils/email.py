import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from ..core.config import settings

def send_violation_email(
    emp_email: str,
    manager_email: str,
    emp_name: str,
    category: str,
    incident: str,
    penalty_color: str,
    comment: str,
    applied_days: float,
    proof_b64: str = ""
) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False

    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            # Employee email
            if emp_email:
                msg = MIMEMultipart()
                msg["From"] = settings.SMTP_USER
                msg["To"] = emp_email
                msg["Subject"] = f"Disciplinary Action: {penalty_color} Card"
                body = f"Dear {emp_name},\n\nIncident: {incident} ({category})\nPenalty: {penalty_color}\nNote: {comment}"
                msg.attach(MIMEText(body, "plain"))
                if proof_b64:
                    img = MIMEImage(proof_b64.encode(), name="proof.jpg")
                    msg.attach(img)
                server.sendmail(settings.SMTP_USER, emp_email, msg.as_string())

            # Manager email
            if manager_email:
                msg = MIMEMultipart()
                msg["From"] = settings.SMTP_USER
                msg["To"] = manager_email
                msg["Subject"] = f"Manager Alert - {emp_name} received {penalty_color}"
                body = f"Employee {emp_name} received {penalty_color} penalty.\nIncident: {incident}"
                msg.attach(MIMEText(body, "plain"))
                if proof_b64:
                    img = MIMEImage(proof_b64.encode(), name="proof.jpg")
                    msg.attach(img)
                server.sendmail(settings.SMTP_USER, manager_email, msg.as_string())
        return True
    except Exception:
        return False
