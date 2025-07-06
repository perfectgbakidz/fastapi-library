from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Book, Loan, User
from datetime import date

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total_books": db.query(Book).count(),
        "borrowed_books": db.query(Loan).filter(Loan.returned == False).count(),
        "overdue_books": db.query(Loan).filter(Loan.returned == False, Loan.due_date < date.today()).count(),
        "active_users": db.query(User).count()
    }

@router.get("/overdue")
def get_overdue_loans(db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.returned == False, Loan.due_date < date.today()).all()