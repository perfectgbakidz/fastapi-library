from pydantic import BaseModel
from datetime import date
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int

class BookCreate(BookBase): pass
class BookUpdate(BookBase): pass

class Book(BookBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    matric_no: str
    department: str

class UserCreate(UserBase): pass
class UserUpdate(UserBase): pass

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Loan(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_on: date
    due_date: date
    returned: bool
    class Config:
        from_attributes = True