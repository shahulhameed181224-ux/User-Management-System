from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
import os, shutil, uuid

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import timedelta

import schemas, models, crud

from security import create_access_token

from database import SessionLocal, engine, get_db

from documents import router as documents_router

from dependencies import (
    admin_required,
    manager_required, 
    get_current_user
    )

from schemas import (
    UserCreate,
    UserResponse,

    PropertyCreate,
    PropertyResponse,

    UserPropertySummary
)

from crud import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,

    create_property,
    get_properties,
    get_property,
    update_property,
    delete_property,

    get_user_property_summary,
    get_tenant_property_summary,
    get_tenant_users,

    authenticate_user
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User Management System using FastAPI and PostgreSQL"
)
# Mount Static & Upload Folders
UPLOAD_DIR = "static/uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
def home():
    return RedirectResponse(url="/login"
    )

# Login Page
@app.get("/login", response_class=HTMLResponse, tags=["login"])
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )

@app.post("/login", tags=["login"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": user.email_id,
            "role": user.role
        },
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# User Page
@app.get("/users-page", response_class=HTMLResponse, tags=["users"])
def users_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"tags": ["users"]}
    )

# Property Page
@app.get("/properties-page", response_class=HTMLResponse, tags=["properties"])
def properties_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="properties.html",
        context={"tags": ["properties"]}
    )

# Dashboard Page
@app.get("/dashboard", response_class=HTMLResponse, tags=["dashboard"])
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"tags": ["dashboard"]}
    )
# Documents Page
@app.get("/documents-page", response_class=HTMLResponse, tags=["documents"])
def documents_page(request: Request):
    return templates.TemplateResponse(name="documents.html", request=request)



# Tenant Summary endpoint
@app.get(
    "/tenant-summary",
    response_model=list[schemas.TenantSummary]
)
def tenant_summary(
    db: Session = Depends(get_db)
):
    return crud.get_tenant_summary(db)

# User Property Counts endpoint
@app.get(
    "/user-property-counts",
    response_model=list[schemas.UserPropertyCount]
)
def user_property_counts(
    db: Session = Depends(get_db)
):
    return crud.get_user_property_counts(db)
# USER APIs

# Create User
@app.post(
    "/users",
    dependencies=[Depends(get_current_user)],
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
    dependencies=[Depends(get_current_user)],
    response_model=list[UserResponse],tags=["users"]
)
def all_users(
    db: Session = Depends(get_db)
):
    return get_users(db)


# Get Single User
@app.get(
    "/users/{user_id}",
    dependencies=[Depends(get_current_user)],
    response_model=UserResponse,tags=["users"]
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
    dependencies=[Depends(get_current_user)],
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
@app.delete("/users/{user_id}", tags=["users"], dependencies=[Depends(get_current_user)])
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

# USER PROPERTY SUMMARY

@app.get(
    "/users/{user_id}/property-summary",
    dependencies=[Depends(get_current_user)],
    response_model=UserPropertySummary,
    tags=["users"]
)
def user_property_summary(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_user_property_summary(
        db,
        user_id
    )

# user property count
@app.get("/users-with-property-counts")
def users_with_property_counts(
    db: Session = Depends(get_db)
):

    return crud.get_users_with_property_counts(db)

@app.get("/user-property-counts")
def user_property_counts(
    db: Session = Depends(get_db)
):
    return crud.get_user_property_counts(db)
# Property APIs

# Create Property
@app.post(
    "/properties",
    dependencies=[Depends(get_current_user)],
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,tags=["properties"]
)
def add_property(
    property: PropertyCreate,
    db: Session = Depends(get_db)
):
    return create_property(db, property)

# Get All Properties
@app.get(
    "/properties",
    dependencies=[Depends(get_current_user)],
    response_model=list[PropertyResponse],tags=["properties"]
)
def all_properties(
    db: Session = Depends(get_db)
):
    return get_properties(db)

# Get Single Property
@app.get(
    "/properties/{property_id}",
    dependencies=[Depends(get_current_user)],
    response_model=PropertyResponse,tags=["properties"]
)
def single_property(
    property_id: UUID,
    db: Session = Depends(get_db)
):
    property = get_property(
        db,
        property_id
    )

    if not property:
        raise HTTPException(
            status_code=404,
            detail="Property Not Found"
        )

    return property

# Update Property
@app.put(
    "/properties/{property_id}",
    dependencies=[Depends(get_current_user)],
    response_model=PropertyResponse,tags=["properties"]
)
def modify_property(
    property_id: UUID,
    property: PropertyCreate,
    db: Session = Depends(get_db)
):
    updated = update_property(
        db,
        property_id,
        property
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Property Not Found"
        )

    return updated

# Delete Property
@app.delete("/properties/{property_id}", tags=["properties"], dependencies=[Depends(get_current_user)])
def remove_property(
    property_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = delete_property(
        db,
        property_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Property Not Found"
        )

    return {
        "message": "Property Deleted Successfully"
    }

# Documents API
@app.post("/documents/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    property_code: str = Form(...),
    property_address: str = Form(None),
    document_type: models.DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_filename = f"{property_code}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    web_path_url = f"/static/uploaded_documents/{unique_filename}"

    doc_in = schemas.DocumentCreate(
        property_code=property_code,
        property_address=property_address,
        document_type=document_type,
        path_url=web_path_url,
        created_by=getattr(current_user, "username", "Admin")
    )
    return crud.create_property_document(db=db, doc_data=doc_in)

@app.get("/documents/by-property/{property_code}")
def get_property_documents(property_code: str, db: Session = Depends(get_db)):
    return crud.get_documents_by_property_code(db=db, property_code=property_code)

@app.delete("/documents/{document_id}")
def remove_document(
    document_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_property_document(db=db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}
