import base64
import os
import re
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .penalties import PENALTY_MAP

SENDER_EMAIL = os.environ.get("EMAIL", "")
SENDER_PASSWORD = os.environ.get("PASSWORD", "")
HR_MANAGER_EMAIL = os.environ.get("HR_MANAGER_EMAIL", SENDER_EMAIL)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _valid(addr: str) -> bool:
    return bool(addr and _EMAIL_RE.match(addr.strip()))


def _attach_proof(msg: MIMEMultipart, proof_b64: str) -> None:
    if not proof_b64:
        return
    try:
        img_data = base64.b64decode(proof_b64)
        msg.attach(MIMEImage(img_data, name="proof.jpg"))
    except Exception:
        pass


def send_violation_emails(
    *,
    emp_email: str,
    manager_email: str,
    emp_name: str,
    category: str,
    incident: str,
    penalty_color: str,
    penalty_label: str,
    applied_days: float,
    comment: str,
    proof_b64: str = "",
) -> tuple[bool, str]:
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "SMTP credentials not configured (set EMAIL/PASSWORD env vars)."

    p = PENALTY_MAP.get(penalty_color, {})
    is_invest = penalty_color == "Investigation"
    badge = p.get("badge", "")

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as srv:
            srv.login(SENDER_EMAIL, SENDER_PASSWORD)

            if _valid(emp_email):
                msg = MIMEMultipart()
                msg["From"] = SENDER_EMAIL
                msg["To"] = emp_email
                msg["Subject"] = (
                    f"URGENT: Suspension Notice \u2014 {emp_name}"
                    if is_invest
                    else f"Disciplinary Action: {badge} {penalty_color} Card"
                )
                if is_invest:
                    body = (
                        f"Dear {emp_name},\n\n"
                        f"You are hereby SUSPENDED pending an investigation.\n\n"
                        f"  Incident : {incident} ({category})\n"
                        f"  HR Notes : {comment}\n\n"
                        f"HR will contact you with further instructions.\n"
                        f"Do NOT report to the office until notified."
                    )
                else:
                    body = (
                        f"Dear {emp_name},\n\n"
                        f"A disciplinary action has been recorded on your file:\n\n"
                        f"  Incident : {incident} ({category})\n"
                        f"  Penalty  : {penalty_label}\n"
                        f"  HR Notes : {comment}\n\n"
                        f"Please adhere to company policies to avoid further escalation.\n\n"
                        f"Human Resources Department"
                    )
                msg.attach(MIMEText(body, "plain", "utf-8"))
                _attach_proof(msg, proof_b64)
                srv.sendmail(SENDER_EMAIL, [emp_email], msg.as_string())

            if _valid(manager_email):
                mgr = MIMEMultipart()
                mgr["From"] = SENDER_EMAIL
                mgr["To"] = manager_email
                mgr["Subject"] = (
                    f"URGENT: Employee Suspended \u2014 {emp_name}"
                    if is_invest
                    else f"Manager Notice \u2014 {emp_name} | {badge} {penalty_color}"
                )
                mgr_body = (
                    f"Dear Manager,\n\n"
                    f"Your team member {emp_name} has received a disciplinary penalty.\n\n"
                    f"  Incident : {incident} ({category})\n"
                    f"  Penalty  : {penalty_label}\n"
                    f"  Notes    : {comment}\n"
                )
                if is_invest:
                    mgr_body += (
                        "\n\nIMPORTANT: This employee is SUSPENDED. "
                        "Do NOT allow them on-site until HR clearance is issued."
                    )
                    recipients = list({manager_email, HR_MANAGER_EMAIL} - {""})
                else:
                    recipients = [manager_email]
                mgr.attach(MIMEText(mgr_body, "plain", "utf-8"))
                _attach_proof(mgr, proof_b64)
                srv.sendmail(SENDER_EMAIL, recipients, mgr.as_string())

        return True, "Emails sent."

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed."
    except smtplib.SMTPException as exc:
        return False, f"SMTP error: {exc}"
    except Exception as exc:
        return False, f"Unexpected error: {exc}"
