from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from uuid import UUID

from database import SessionLocal, engine

from schemas import (
    UserCreate,
    UserResponse,
    TenantCreate,
    TenantResponse
)

from crud import (
    create_tenant,
    get_tenants,
    get_tenant,
    update_tenant,
    delete_tenant,
    
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user
)

import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User Management System using FastAPI and PostgreSQL"
)

# Static Folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates Folder
templates = Jinja2Templates(directory="templates")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HTML PAGES

# Home Page
@app.get("/", response_class=HTMLResponse, tags=["home"])
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# Tenant Page
@app.get("/tenants-page", response_class=HTMLResponse, tags=["tenants"])
def tenants_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="tenants.html",
        context={"tags": ["tenants"]}
    )


# User Page
@app.get("/users-page", response_class=HTMLResponse, tags=["users"])
def users_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"tags": ["users"]}
    )

# TENANT APIs

# Create Tenant
@app.post(
    "/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,tags=["tenants"]
)
def add_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    return create_tenant(db, tenant)


# Get All Tenants
@app.get(
    "/tenants",
    response_model=list[TenantResponse],tags=["tenants"]
)
def all_tenants(
    db: Session = Depends(get_db)
):
    return get_tenants(db)


# Get Single Tenant
@app.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,tags=["tenants"]
)
def single_tenant(
    tenant_id: UUID,
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
    response_model=TenantResponse,tags=["tenants"]
)
def modify_tenant(
    tenant_id: UUID,
    tenant: TenantCreate,
    db: Session = Depends(get_db)
):
    updated = update_tenant(
        db,
        tenant_id,
        tenant
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Tenant Not Found"
        )

    return updated


# Delete Tenant
@app.delete("/tenants/{tenant_id}", tags=["tenants"])
def remove_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = delete_tenant(
        db,
        tenant_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tenant Not Found"
        )

    return {
        "message": "Tenant Deleted Successfully"
    }

# USER APIs

# Create User
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,tags=["users"]
)
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)


# Get All Users
@app.get(
    "/users",
    response_model=list[UserResponse],tags=["users"]
)
def all_users(
    db: Session = Depends(get_db)
):
    return get_users(db)


# Get Single User
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,tags=["users"]
)
def single_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = get_user(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return user


# Update User
@app.put(
    "/users/{user_id}",
    response_model=UserResponse,tags=["users"]
)
def modify_user(
    user_id: UUID,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    updated = update_user(
        db,
        user_id,
        user
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return updated


# Delete User
@app.delete("/users/{user_id}", tags=["users"])
def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = delete_user(
        db,
        user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {
        "message": "User Deleted Successfully"
    }