from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


# === BOOK SCHEMAS ===
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    quantity: int = Field(ge=0)
    description: Optional[str] = None
    category: Optional[str] = None
    cover_image_url: Optional[str] = None

class BookCreate(BookBase): ...
class BookUpdate(BookBase): ...

class Book(BookBase):
    id: int
    available_quantity: Optional[int] = None  # NEW calculated field

    class Config:
        from_attributes = True


# === USER SCHEMAS ===
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
    profile_picture_url: Optional[str] = None
    class Config:
        from_attributes = True


# === AUTH SCHEMAS ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None


# === PASSWORD SCHEMA ===
class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# === LOAN SCHEMAS ===

# For internal use, includes all fields
class Loan(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrowed_on: Optional[date]
    due_date: Optional[date]
    return_date: Optional[date] = None
    returned: bool
    status: str  # "pending", "approved", "rejected"

    class Config:
        from_attributes = True

# For embedding in user details
class LoanOut(BaseModel):
    id: int
    book_id: int
    borrowed_on: Optional[date]
    due_date: Optional[date]
    return_date: Optional[date]
    returned: bool
    status: str

    class Config:
        from_attributes = True


# === EXTENDED USER FOR ADMINS ===

class LoanOutExtended(BaseModel):
    id: int
    book_id: int
    book_title: str
    borrowed_on: Optional[date]
    due_date: Optional[date]
    return_date: Optional[date]
    status: str

    class Config:
        from_attributes = True



class UserOutExtended(BaseModel):
    id: int
    name: str
    matric_no: str
    department: str
    role: str
    profile_picture_url: Optional[str] = None
    loans: List[LoanOutExtended]
    login_history: List[dict] = []

    class Config:
        from_attributes = True


class HoldResponse(BaseModel):
    detail: str


class LoanRequest(BaseModel):
    book_id: int

class ReturnBookRequest(BaseModel):
    book_id: int

