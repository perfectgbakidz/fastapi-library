from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import User, UserUpdate
from dependencies import get_current_admin, get_current_user

router = APIRouter()

@router.get("/", response_model=list[User], dependencies=[Depends(get_current_admin)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/{id}", response_model=User, dependencies=[Depends(get_current_admin)])
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

@router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}
