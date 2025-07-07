from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User
from utils import verify_password, get_password_hash, create_access_token
from schemas import UserCreate, Token

router = APIRouter()

ADMIN_CODE = "SUPERADMIN123"

@router.post("/register", response_model=Token, summary="Register user (student/admin)")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.matric_no == user_in.matric_no).first():
        raise HTTPException(status_code=400, detail="Matric number already registered")
    role = user_in.role or "student"
    if role == "admin":
        if user_in.admin_code != ADMIN_CODE:
            raise HTTPException(status_code=403, detail="Invalid admin code")
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        name=user_in.name,
        matric_no=user_in.matric_no,
        department=user_in.department,
        role=role,
        hashed_password=hashed_pwd
    )
    db.add(user)
    db.commit()
    access_token = create_access_token({"sub": user.matric_no})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token, summary="Login and get JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.matric_no == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = create_access_token({"sub": user.matric_no})
    return Token(access_token=access_token)


@router.post("/forgot-password")
def forgot_password(email: str):
    # Placeholder: send reset email logic
    return {"detail": "Password reset email sent."}


@router.post("/reset-password")
def reset_password(token: str, new_password: str):
    # Placeholder: validate token and update password
    return {"detail": "Password has been reset successfully."}
