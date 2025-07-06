from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Book
from schemas import BookCreate, BookUpdate, Book
from dependencies import get_current_user, get_current_admin

router = APIRouter()

@router.get("/", response_model=list[Book])
def get_books(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Book).all()

@router.post("/", response_model=Book, dependencies=[Depends(get_current_admin)])
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/{id}", response_model=Book, dependencies=[Depends(get_current_admin)])
def update_book(id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).get(id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for k, v in book.dict().items():
        setattr(db_book, k, v)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{id}", dependencies=[Depends(get_current_admin)])
def delete_book(id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).get(id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}
