from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Book, Loan, User
from datetime import date
from dependencies import get_current_admin

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total_books": db.query(Book).count(),
        "borrowed_books": db.query(Loan).filter(Loan.returned == False).count(),
        "overdue_books": db.query(Loan).filter(Loan.returned == False, Loan.due_date < date.today()).count(),
        "total_students": db.query(User).filter(User.role == "student").count(),
        "returned_books": db.query(Loan).filter(Loan.returned == True).count()
    }


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    total_books = db.query(Book).count()
    borrowed_books = db.query(Loan).filter(Loan.returned == False).count()
    returned_books = db.query(Loan).filter(Loan.returned == True).count()
    overdue_books = db.query(Loan).filter(Loan.returned == False, Loan.due_date < date.today()).count()
    total_students = db.query(User).filter(User.role == "student").count()
    pending_loans = db.query(Loan).filter(Loan.status == "pending").count()

    return {
        "total_books": total_books,
        "borrowed_books": borrowed_books,
        "overdue_books": overdue_books,
        "total_students": total_students,
        "returned_books": returned_books,
        "pending_loans": pending_loans
    }



@router.get("/overdue")
def get_overdue_loans(db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.returned == False, Loan.due_date < date.today()).all()
