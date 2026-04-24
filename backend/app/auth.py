import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

HR_ADMIN_PASSWORD = os.environ.get("HR_ADMIN_PASSWORD", "admin123")
HR_ADMIN_USERNAME = os.environ.get("HR_ADMIN_USERNAME", "hr")

_security = HTTPBasic()


def require_admin(creds: HTTPBasicCredentials = Depends(_security)) -> str:
    user_ok = secrets.compare_digest(creds.username, HR_ADMIN_USERNAME)
    pass_ok = secrets.compare_digest(creds.password, HR_ADMIN_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return creds.username
