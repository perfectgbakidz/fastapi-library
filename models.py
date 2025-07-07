from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base




class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, default=1)

    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    matric_no = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, default="student")
    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)  # ✅ Add this line

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrowed_on = Column(Date)
    due_date = Column(Date)
    returned = Column(Boolean, default=False)
    status = Column(String, default="pending")
    request_date = Column(Date)
    return_date = Column(Date, nullable=True)
    user = relationship("User")
    book = relationship("Book")


class HoldRequest(Base):
    __tablename__ = "hold_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    request_date = Column(Date)

    user = relationship("User")
    book = relationship("Book")
