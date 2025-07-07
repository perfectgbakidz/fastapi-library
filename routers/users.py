from fastapi import APIRouter, Depends, HTTPException , UploadFile, File
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User, Loan
from schemas import User as UserSchema, UserUpdate, PasswordChange, UserOutExtended
from dependencies import get_current_admin, get_current_user
from utils import get_password_hash, verify_password



router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserSchema)
def update_me(user_up: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.name = user_up.name or current_user.name
    current_user.department = user_up.department or current_user.department
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/password")
def change_password(data: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=403, detail="Incorrect current password")
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}

@router.get("/", response_model=list[UserSchema], dependencies=[Depends(get_current_admin)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/{id}", response_model=UserSchema, dependencies=[Depends(get_current_admin)])
def update_user(id: int, user_up: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_up.role:
        user.role = user_up.role
    user.name = user_up.name or user.name
    user.department = user_up.department or user.department
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}/details", response_model=UserOutExtended, dependencies=[Depends(get_current_admin)])
def get_user_details(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    loans = db.query(Loan).filter(Loan.user_id == user_id).all()

    loans_data = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "book_title": loan.book.title,
            "borrowed_on": loan.borrowed_on,
            "due_date": loan.due_date,
            "return_date": loan.return_date,
            "status": loan.status,
        }
        for loan in loans
    ]

    return {
        **user.__dict__,
        "loans": loans_data,
        "login_history": []  # Optional future expansion
    }


@router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}



UPLOAD_DIR = "static/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/me/picture", response_model=UserSchema)
def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename = f"{current_user.id}_{file.filename.replace(' ', '_').replace('/', '_')}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    current_user.profile_picture_url = f"/{filepath}"
    db.commit()
    db.refresh(current_user)
    return current_user
