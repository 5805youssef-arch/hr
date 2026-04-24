import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
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
        print("❌ SMTP Setup Missing: Please check your .env file for SMTP credentials.")
        return False

    try:
        # Decode the Base64 image ONCE so we can attach it to both emails
        img_data = None
        if proof_b64:
            try:
                if "," in proof_b64:
                    proof_b64 = proof_b64.split(",")[1]
                img_data = base64.b64decode(proof_b64)
            except Exception as img_err:
                print(f"⚠️ Failed to decode image: {img_err}")

        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            # ---------------------------------------------------------
            # 1. Send Professional Email to Employee
            # ---------------------------------------------------------
            if emp_email:
                msg_emp = MIMEMultipart()
                msg_emp["From"] = settings.SMTP_USER
                msg_emp["To"] = emp_email
                msg_emp["Subject"] = f"Disciplinary Action: {penalty_color} Card"
                
                body_emp = (
                    f"Dear {emp_name},\n\n"
                    f"A disciplinary action has been recorded on your file:\n\n"
                    f"  Incident : {incident} ({category})\n"
                    f"  Penalty  : {penalty_color}\n"
                    f"  HR Notes : {comment}\n\n"
                    f"Please adhere to company policies to avoid further escalation.\n\n"
                    f"Human Resources Department"
                )
                msg_emp.attach(MIMEText(body_emp, "plain"))
                
                # Attach the image if it exists
                if img_data:
                    msg_emp.attach(MIMEImage(img_data, name="proof.jpg"))

                server.sendmail(settings.SMTP_USER, emp_email, msg_emp.as_string())
                print(f"✅ Professional Email sent to Employee: {emp_email}")

            # ---------------------------------------------------------
            # 2. Send Professional Email to Manager
            # ---------------------------------------------------------
            if manager_email:
                msg_mgr = MIMEMultipart()
                msg_mgr["From"] = settings.SMTP_USER
                msg_mgr["To"] = manager_email
                msg_mgr["Subject"] = f"Manager Alert - {emp_name} received {penalty_color}"
                
                body_mgr = (
                    f"Dear Manager,\n\n"
                    f"Your team member {emp_name} has received a disciplinary penalty.\n\n"
                    f"  Incident : {incident} ({category})\n"
                    f"  Penalty  : {penalty_color}\n"
                    f"  Notes    : {comment}"
                )
                msg_mgr.attach(MIMEText(body_mgr, "plain"))
                
                # Attach the exact same image to the manager's email
                if img_data:
                    msg_mgr.attach(MIMEImage(img_data, name="proof.jpg"))

                server.sendmail(settings.SMTP_USER, manager_email, msg_mgr.as_string())
                print(f"✅ Professional Email sent to Manager: {manager_email}")
                
        return True
    except Exception as e:
        print(f"❌ SMTP Error Failed to send email: {e}")
        return False