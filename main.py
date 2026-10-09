import os
import shutil
import uuid
import io
import phonenumbers
from fastapi.responses import FileResponse
from datetime import timedelta
from uuid import UUID
from pypdf import PdfReader, PdfWriter

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request,
    UploadFile,
    File,
    Form
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import schemas
import models
import crud
from database import engine, get_db
from security import create_access_token
from dependencies import get_current_user

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User & Property Management System using FastAPI and PostgreSQL"
)

# Upload directory setup
UPLOAD_DIR = "static/uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# HTML TEMPLATE ROUTES

@app.get("/", response_class=HTMLResponse, tags=["home"])
def home():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse, tags=["login"])
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/users-page", response_class=HTMLResponse, tags=["users"])
def users_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"tags": ["users"]}
    )


@app.get("/properties-page", response_class=HTMLResponse, tags=["properties"])
def properties_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="properties.html",
        context={"tags": ["properties"]}
    )


@app.get("/dashboard", response_class=HTMLResponse, tags=["dashboard"])
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"tags": ["dashboard"]}
    )


@app.get("/documents-page", response_class=HTMLResponse, tags=["documents"])
def documents_page(request: Request):
    return templates.TemplateResponse(request=request, name="documents.html")

# AUTHENTICATION

@app.post("/login", tags=["login"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": user.email_id,
            "role": user.role,
            "user_name": user.user_name
        },
        expires_delta=timedelta(minutes=60)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.user_name
    }

# TENANT APIS (FULL CRUD & VERIFICATION)

@app.post(
    "/tenants",
    response_model=schemas.TenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def create_tenant(
    tenant_in: schemas.TenantCreate,
    db: Session = Depends(get_db)
):
    """Creates a new tenant directly."""
    return crud.create_tenant(db, tenant_in)


@app.get(
    "/tenants",
    response_model=list[schemas.TenantResponse],
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def list_tenants(db: Session = Depends(get_db)):
    """Retrieves all registered tenants."""
    return crud.get_all_tenants(db)


@app.get(
    "/tenants/{tenant_id}",
    response_model=schemas.TenantResponse,
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def single_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Retrieves a single tenant by UUID."""
    return crud.get_tenant(db, tenant_id)


@app.put(
    "/tenants/{tenant_id}",
    response_model=schemas.TenantResponse,
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def modify_tenant(
    tenant_id: UUID,
    tenant_in: schemas.TenantCreate,
    db: Session = Depends(get_db)
):
    """Updates tenant details (e.g. name or type)."""
    return crud.update_tenant(db, tenant_id, tenant_in)


@app.delete(
    "/tenants/{tenant_id}",
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def remove_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    """Deletes a tenant and cascades to all associated users/properties."""
    crud.delete_tenant(db, tenant_id)
    return {"message": "Tenant deleted successfully"}


@app.post(
    "/tenants/verify-or-create",
    response_model=schemas.TenantResponse,
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def verify_or_create_tenant(
    tenant_in: schemas.TenantCreate,
    db: Session = Depends(get_db)
):
    return crud.get_or_create_tenant(db, tenant_in)


@app.get(
    "/tenants/check/{tenant_name}",
    response_model=schemas.TenantCheckResponse,
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def check_tenant(
    tenant_name: str,
    db: Session = Depends(get_db)
):
    return crud.check_tenant_status(db, tenant_name)


@app.get(
    "/tenant-summary",
    response_model=list[schemas.TenantSummary],
    dependencies=[Depends(get_current_user)],
    tags=["tenants"]
)
def tenant_summary(db: Session = Depends(get_db)):
    return crud.get_tenant_summary(db)

# USER APIS

@app.post(
    "/users",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def add_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Creates a user under a target tenant. Automatically generates a unique user_name."""
    return crud.create_user(db, user)


@app.get(
    "/users",
    response_model=list[schemas.UserResponse],
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def all_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@app.get(
    "/users/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def single_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user


@app.put(
    "/users/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def modify_user(
    user_id: UUID,
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    updated = crud.update_user(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User Not Found")
    return updated


@app.delete(
    "/users/{user_id}",
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User Not Found")
    return {"message": "User Deleted Successfully"}


@app.get(
    "/users/by-username/{user_name}/property-summary",
    response_model=schemas.UserPropertySummary,
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def user_property_summary(
    user_name: str,
    db: Session = Depends(get_db)
):
    return crud.get_user_property_summary(db, user_name)


@app.get(
    "/users-with-property-counts",
    response_model=list[schemas.UserPropertyCount],
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def users_with_property_counts(db: Session = Depends(get_db)):
    return crud.get_users_with_property_counts(db)


@app.get(
    "/user-property-counts",
    response_model=list[schemas.UserPropertyCount],
    dependencies=[Depends(get_current_user)],
    tags=["users"]
)
def user_property_counts(db: Session = Depends(get_db)):
    return crud.get_user_property_counts(db)

# PROPERTY APIS

@app.post(
    "/properties",
    response_model=schemas.PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def add_property(
    property_in: schemas.PropertyCreate,
    db: Session = Depends(get_db)
):
    return crud.create_property(db, property_in)


@app.get(
    "/properties",
    response_model=list[schemas.PropertyResponse],
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def all_properties(db: Session = Depends(get_db)):
    return crud.get_properties(db)


@app.get(
    "/properties/{property_id}",
    response_model=schemas.PropertyResponse,
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def single_property(
    property_id: UUID,
    db: Session = Depends(get_db)
):
    property_data = crud.get_property(db, property_id)
    if not property_data:
        raise HTTPException(status_code=404, detail="Property Not Found")
    return property_data


@app.get(
    "/properties/by-user/{user_name}",
    response_model=list[schemas.PropertyResponse],
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def get_properties_by_user(
    user_name: str,
    db: Session = Depends(get_db)
):
    return crud.get_properties_by_username(db, user_name)


@app.put(
    "/properties/{property_id}",
    response_model=schemas.PropertyResponse,
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def modify_property(
    property_id: UUID,
    property_in: schemas.PropertyCreate,
    db: Session = Depends(get_db)
):
    updated = crud.update_property(db, property_id, property_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Property Not Found")
    return updated


@app.delete(
    "/properties/{property_id}",
    dependencies=[Depends(get_current_user)],
    tags=["properties"]
)
def remove_property(
    property_id: UUID,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_property(db, property_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Property Not Found")
    return {"message": "Property Deleted Successfully"}

# DOCUMENTS APIS

@app.post("/documents/{document_id}/verify-and-view", tags=["documents"])
def verify_and_view_document(
    document_id: int,
    phone_number: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch the document
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # 2. Trace Property -> User
    prop = db.query(models.Property).filter(
        models.Property.property_code == doc.property_code
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Associated property not found.")

    user = db.query(models.User).filter(
        models.User.user_name == prop.user_name
    ).first()
    if not user or not user.phone_number:
        raise HTTPException(status_code=400, detail="Assigned user or phone number not found.")

    # 3. Normalize and compare phone numbers
    def normalize_phone(num: str):
        try:
            parsed = phonenumbers.parse(num.strip(), None)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            return "".join(filter(str.isdigit, num))

    if normalize_phone(phone_number) != normalize_phone(user.phone_number):
        raise HTTPException(status_code=403, detail="Phone number does not match property owner.")

    # 4. Resolve file path and return the PDF
    # doc.path_url is like "/static/uploaded_documents/filename.pdf"
    relative_path = doc.path_url.lstrip("/")
    if not os.path.exists(relative_path):
        raise HTTPException(status_code=404, detail="File not found on server disk.")

    return FileResponse(
        path=relative_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )

@app.get("/documents/by-property/{property_code}", tags=["documents"])
def get_property_documents(property_code: str, db: Session = Depends(get_db)):
    return crud.get_documents_by_property_code(db=db, property_code=property_code)


@app.delete("/documents/{document_id}", tags=["documents"])
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_property_document(db=db, document_id=document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}