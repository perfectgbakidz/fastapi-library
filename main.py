from fastapi import FastAPI
from routers import books, users, loans, dashboard
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API")

# Include routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])