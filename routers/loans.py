from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Loan, Book
from datetime import date, timedelta

router = APIRouter()

@router.get("/active")
def get_active_loans(db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.returned == False).all()

@router.post("/borrow")
def borrow_book(user_id: int, book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).get(book_id)
    if not book or book.quantity <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    loan = Loan(
        user_id=user_id,
        book_id=book_id,
        borrowed_on=date.today(),
        due_date=date.today() + timedelta(days=14),
        returned=False
    )
    db.add(loan)
    book.quantity -= 1
    db.commit()
    return {"detail": "Book borrowed"}

@router.post("/{id}/return")
def return_book(id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).get(id)
    if not loan or loan.returned:
        raise HTTPException(status_code=404, detail="Loan not found or already returned")
    loan.returned = True
    book = db.query(Book).get(loan.book_id)
    book.quantity += 1
    db.commit()
    fine = 0
    if date.today() > loan.due_date:
        fine = (date.today() - loan.due_date).days * 50
    return {"detail": "Book returned", "fine": fine}