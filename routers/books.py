
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Book, Loan, HoldRequest, User
from schemas import Book as BookSchema
from dependencies import get_current_user, get_current_admin
from typing import List
from datetime import date
import os
from uuid import uuid4
from shutil import copyfileobj

router = APIRouter()

UPLOAD_DIR = "static/book-covers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{book_id}/hold")
def place_hold(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can place holds.")

    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    active_loans = db.query(Loan).filter(
        Loan.book_id == book_id,
        Loan.status == "approved",
        Loan.returned == False
    ).count()

    available_quantity = book.quantity - active_loans

    if available_quantity > 0:
        raise HTTPException(status_code=400, detail="Book is currently available. No need to hold.")

    existing_hold = db.query(HoldRequest).filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing_hold:
        raise HTTPException(status_code=400, detail="You have already placed a hold on this book.")

    hold = HoldRequest(
        user_id=current_user.id,
        book_id=book_id,
        request_date=date.today()
    )
    db.add(hold)
    db.commit()

    return {"detail": f"You have been placed on the waitlist for '{book.title}'."}


@router.get("/", response_model=List[BookSchema])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    result = []

    for book in books:
        borrowed = db.query(Loan).filter(Loan.book_id == book.id, Loan.status == "approved", Loan.returned == False).count()
        result.append(
            BookSchema(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                quantity=book.quantity,
                description=book.description,
                category=book.category,
                cover_image_url=book.cover_image_url,
                available_quantity=book.quantity - borrowed
            )
        )
    return result

@router.get("/{book_id}", response_model=BookSchema)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    borrowed = db.query(Loan).filter(Loan.book_id == book.id, Loan.status == "approved", Loan.returned == False).count()

    return BookSchema(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        description=book.description,
        category=book.category,
        cover_image_url=book.cover_image_url,
        available_quantity=book.quantity - borrowed
    )

@router.post("/", response_model=BookSchema, dependencies=[Depends(get_current_admin)])
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    cover_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = cover_image.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    filename = f"{uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        copyfileobj(cover_image.file, f)

    cover_url = f"/static/book-covers/{filename}"

    db_book = Book(
        title=title,
        author=author,
        isbn=isbn,
        quantity=quantity,
        description=description,
        category=category,
        cover_image_url=cover_url
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/{id}", response_model=BookSchema, dependencies=[Depends(get_current_admin)])
def update_book(
    id: int,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    cover_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    db_book = db.query(Book).get(id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = title
    db_book.author = author
    db_book.isbn = isbn
    db_book.quantity = quantity
    db_book.description = description
    db_book.category = category

    if cover_image:
        ext = cover_image.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Unsupported image format")

        if db_book.cover_image_url:
            try:
                old_path = db_book.cover_image_url.lstrip("/")
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass

        filename = f"{uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            copyfileobj(cover_image.file, f)
        db_book.cover_image_url = f"/static/book-covers/{filename}"

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
