from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from uuid import UUID

from database import SessionLocal
from database import engine

from schemas import UserCreate
from schemas import UserResponse

from crud import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user
)

import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User Management Service using FastAPI and PostgreSQL"
)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home API
@app.get("/", tags=["Home"])
def home():
    return {
        "message": "User Service API Running Successfully"
    }


# Create User
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"]
)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)


# Get All Users
@app.get(
    "/users",
    response_model=list[UserResponse],
    tags=["Users"]
)
def all_users(
    db: Session = Depends(get_db)
):
    return get_users(db)


# Get Single User
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"]
)
def single_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return user


# Update User
@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"]
)
def modify_user(
    user_id: UUID,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    updated_user = update_user(
        db,
        user_id,
        user
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return updated_user


# Delete User
@app.delete(
    "/users/{user_id}",
    tags=["Users"]
)
def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = delete_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {
        "message": "User Deleted Successfully"
    }