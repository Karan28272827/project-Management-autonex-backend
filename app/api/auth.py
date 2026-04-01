"""
Authentication API: signup, login, logout, me.
"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from jose import ExpiredSignatureError, JWTError

from app.db.database import get_db
from app.models.user import User
from app.models.employee import Employee
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    decode_token,
    hash_reset_token,
    blacklist_token,
    is_token_blacklisted,
    get_current_user,
)
from app.services.slack_service import send_slack_reset_link

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Schemas ─────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: Optional[List[str]] = None
    role: Optional[str] = "employee"       # admin, pm, employee


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    portal: Optional[Literal["admin", "pm", "employee"]] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    designation: Optional[str] = None
    employee_id: Optional[int] = None
    skills: Optional[list] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


DESIGNATION_ACCESS = {
    "Admin": "admin",
    "Program Manager": "pm",
    "Annotator/ Reviewer": "employee",
    "Annotator/Reviewer": "employee",
    "Annotator": "employee",
    "Reviewer": "employee",
    "Developer": "employee",
}


def get_user_designation(user: User, db: Session) -> Optional[str]:
    employee = None
    if user.employee_id:
        employee = db.query(Employee).filter(Employee.id == user.employee_id).first()
    if employee is None:
        employee = db.query(Employee).filter(Employee.email == user.email).first()
    if employee and employee.designation:
        return employee.designation
    if user.role == "admin":
        return "Admin"
    return None


def get_access_role(designation: Optional[str], fallback_role: str) -> str:
    return DESIGNATION_ACCESS.get(designation, fallback_role)


def build_user_response(user: User, db: Session) -> UserResponse:
    designation = get_user_designation(user, db)
    access_role = get_access_role(designation, user.role)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=access_role,
        designation=designation,
        employee_id=user.employee_id,
        skills=user.skills,
    )


def get_frontend_base_url(request: Request) -> str:
    return (
        os.getenv("RESET_PASSWORD_FRONTEND_URL")
        or os.getenv("FRONTEND_URL")
        or request.headers.get("origin")
        or "http://localhost:5173"
    ).rstrip("/")


# ── Endpoints ───────────────────────────────────────────────────────

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user. Defaults to 'employee' role."""

    # Check duplicate email
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Only allow 'employee' or 'pm' via signup; admin is seed-only
    role = body.role if body.role in ("employee", "pm") else "employee"

    # Create matching Employee record so they appear in the team
    employee = Employee(
        name=body.name,
        email=body.email,
        employee_type="Full-time",
        designation="Program Manager" if role == "pm" else "Annotator/ Reviewer",
        skills=body.skills or [],
        status="active",
    )
    db.add(employee)
    db.flush()  # get employee.id

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=role,
        employee_id=employee.id,
        skills=body.skills or [],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response_user = build_user_response(user, db)
    token = create_access_token({
        "sub": str(user.id),
        "role": response_user.role,
        "designation": response_user.designation,
        "employee_id": user.employee_id,
    })

    return LoginResponse(token=token, user=response_user)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email + password, returns JWT."""

    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    response_user = build_user_response(user, db)
    if body.portal and response_user.role != body.portal:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. This account must sign in through the {response_user.role} portal.",
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": response_user.role,
        "designation": response_user.designation,
        "employee_id": user.employee_id,
    })

    return LoginResponse(token=token, user=response_user)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    generic_message = "If an account exists for that email, reset instructions have been sent."
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not user.is_active:
        return MessageResponse(message=generic_message)

    employee = None
    if user.employee_id:
        employee = db.query(Employee).filter(Employee.id == user.employee_id).first()
    if employee is None:
        employee = db.query(Employee).filter(Employee.email == user.email).first()

    slack_user_id = getattr(employee, "slack_user_id", None)
    if not slack_user_id:
        return MessageResponse(message=generic_message)

    reset_token, expires_at = create_password_reset_token(user.id)
    user.password_reset_token_hash = hash_reset_token(reset_token)
    user.password_reset_expires_at = expires_at
    db.add(user)
    db.commit()

    reset_link = f"{get_frontend_base_url(request)}/reset-password?token={reset_token}&role={get_access_role(get_user_designation(user, db), user.role)}"

    try:
        await send_slack_reset_link(slack_user_id, reset_link)
    except Exception as exc:
        user.password_reset_token_hash = None
        user.password_reset_expires_at = None
        db.add(user)
        db.commit()
        raise HTTPException(status_code=503, detail="Password reset Slack delivery is unavailable") from exc

    return MessageResponse(message=generic_message)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    body: ResetPasswordRequest,
    token: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset link has expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid reset link")

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid reset link")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid reset link")

    if not user.password_reset_token_hash or not user.password_reset_expires_at:
        raise HTTPException(status_code=400, detail="Invalid reset link")

    if user.password_reset_token_hash != hash_reset_token(token):
        raise HTTPException(status_code=400, detail="Invalid reset link")

    if user.password_reset_expires_at < datetime.utcnow():
        user.password_reset_token_hash = None
        user.password_reset_expires_at = None
        db.add(user)
        db.commit()
        raise HTTPException(status_code=400, detail="Reset link has expired")

    user.password_hash = hash_password(body.password)
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None
    db.add(user)
    db.commit()

    return MessageResponse(message="Password reset successful. You can now sign in with your new password.")


@router.post("/logout")
def logout(request: Request):
    """Invalidate current token."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        blacklist_token(auth_header[7:])
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the currently authenticated user profile."""
    return build_user_response(user, db)


@router.get("/verify")
def verify_token(request: Request):
    """Quick check: is the bearer token still valid?"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"valid": False, "reason": "No token provided"}
    token = auth_header[7:]
    if is_token_blacklisted(token):
        return {"valid": False, "reason": "Token invalidated"}
    return {"valid": True}
