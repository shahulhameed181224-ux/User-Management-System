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

from schemas import (
    UserCreate,
    TenantCreate,
    TenantResponse
)


from crud import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,

    create_tenant,
    get_tenants,
    get_tenant,
    update_tenant,
    delete_tenant
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

# Create Tenant
@app.post(
    "/tenants",
    response_model=TenantResponse,
)
def add_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    return create_tenant(db, tenant)

# Get All Tenants
@app.get(
    "/tenants",
    response_model=list[TenantResponse]
)
def all_tenants(
    db: Session = Depends(get_db)
):
    return get_tenants(db)

# Get Tenant by ID
@app.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse
)
def single_tenant(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    tenant = get_tenant(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant Not Found"
        )

    return tenant

# Update Tenant
@app.put(
    "/tenants/{tenant_id}",
    response_model=TenantResponse
)
def modify_tenant(
    tenant_id: str,
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    updated_tenant = update_tenant(
        db,
        tenant_id,
        tenant
    )

    if not updated_tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant Not Found"
        )

    return updated_tenant

# Delete Tenant
@app.delete("/tenants/{tenant_id}")
def remove_tenant(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    tenant = delete_tenant(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant Not Found"
        )

    return {
        "message": "Tenant Deleted Successfully"
    }