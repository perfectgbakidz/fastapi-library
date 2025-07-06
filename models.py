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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    matric_no = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, default="student")  # 'student' or 'admin'
    hashed_password = Column(String, nullable=False)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrowed_on = Column(Date)
    due_date = Column(Date)
    returned = Column(Boolean, default=False)

    user = relationship("User")
    book = relationship("Book")
