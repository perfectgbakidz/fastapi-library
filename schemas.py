from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int = Field(ge=0)

class BookCreate(BookBase): ...
class BookUpdate(BookBase): ...

class Book(BookBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    matric_no: str
    department: str

class UserCreate(UserBase):
    password: str
    role: str = "student"
    admin_code: Optional[str] = None

class UserUpdate(UserBase):
    role: Optional[str] = None

class User(UserBase):
    id: int
    role: str
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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
