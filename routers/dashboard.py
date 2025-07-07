from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Loan, Book, User
from datetime import date, timedelta
from dependencies import get_current_user, get_current_admin
from schemas import LoanRequest,ReturnBookRequest


router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)])
def get_loans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return db.query(Loan).all()
    return db.query(Loan).filter(Loan.user_id == current_user.id).all()


@router.get("/active", dependencies=[Depends(get_current_admin)])
def get_active_loans(db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.returned == False).all()


@router.post("/request", dependencies=[Depends(get_current_user)])
def request_loan(
    request: LoanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book_id = request.book_id

    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    loan = Loan(
        user_id=current_user.id,
        book_id=book_id,
        request_date=date.today(),
        status="pending",
        returned=False
    )
    db.add(loan)
    db.commit()
    return {"detail": "Loan requested successfully."}


@router.post("/{loan_id}/approve", dependencies=[Depends(get_current_admin)])
def approve_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).get(loan_id)
    if not loan or loan.status != "pending":
        raise HTTPException(status_code=404, detail="Loan not found or already processed")
    
    book = db.query(Book).get(loan.book_id)
    if book.quantity <= 0:
        raise HTTPException(status_code=400, detail="Book out of stock")

    loan.status = "approved"
    loan.borrowed_on = date.today()
    loan.due_date = date.today() + timedelta(days=14)
    book.quantity -= 1
    db.commit()
    return {"detail": "Loan approved."}


@router.post("/{loan_id}/reject", dependencies=[Depends(get_current_admin)])
def reject_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).get(loan_id)
    if not loan or loan.status != "pending":
        raise HTTPException(status_code=404, detail="Loan not found or already processed")
    
    loan.status = "rejected"
    db.commit()
    return {"detail": "Loan rejected."}





@router.post("/return", dependencies=[Depends(get_current_user)])
def return_book(
    request: ReturnBookRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book_id = request.book_id

    loan = db.query(Loan).filter_by(book_id=book_id, user_id=current_user.id, returned=False).first()
    if not loan:
        raise HTTPException(status_code=404, detail="No active loan found")
    
    loan.returned = True
    loan.return_date = date.today()

    book = db.query(Book).get(book_id)
    book.quantity += 1
    db.commit()

    fine = 0
    if date.today() > loan.due_date:
        fine = (date.today() - loan.due_date).days * 50
    
    return {"detail": "Book returned successfully.", "fine": fine}
