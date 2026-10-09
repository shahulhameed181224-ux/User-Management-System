import re
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

import models
import schemas
from models import User, Property, Tenant, TenantType
from security import hash_password, verify_password

# TENANT CRUD OPERATIONS

def get_all_tenants(db: Session):
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()


def get_tenant(db: Session, tenant_id: UUID) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found."
        )
    return tenant


def create_tenant(db: Session, tenant_data: schemas.TenantCreate) -> Tenant:
    cleaned_name = tenant_data.tenant_name.strip()
    existing = db.query(Tenant).filter(
        func.lower(Tenant.tenant_name) == func.lower(cleaned_name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant '{cleaned_name}' already exists."
        )

    tenant = Tenant(
        tenant_name=cleaned_name,
        tenant_type=tenant_data.tenant_type,
        created_by="Admin"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def update_tenant(db: Session, tenant_id: UUID, tenant_data: schemas.TenantCreate) -> Tenant:
    tenant = get_tenant(db, tenant_id)
    cleaned_name = tenant_data.tenant_name.strip()

    # Check for name collision with other tenants
    duplicate = db.query(Tenant).filter(
        func.lower(Tenant.tenant_name) == func.lower(cleaned_name),
        Tenant.id != tenant_id
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant name '{cleaned_name}' is already in use."
        )

    tenant.tenant_name = cleaned_name
    tenant.tenant_type = tenant_data.tenant_type
    tenant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tenant)
    return tenant


def delete_tenant(db: Session, tenant_id: UUID) -> bool:
    tenant = get_tenant(db, tenant_id)
    db.delete(tenant)
    db.commit()
    return True


def get_or_create_tenant(db: Session, tenant_data: schemas.TenantCreate) -> Tenant:
    cleaned_name = tenant_data.tenant_name.strip()
    tenant = db.query(Tenant).filter(
        func.lower(Tenant.tenant_name) == func.lower(cleaned_name)
    ).first()

    if not tenant:
        tenant = Tenant(
            tenant_name=cleaned_name,
            tenant_type=tenant_data.tenant_type,
            created_by="User Registration"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant


def check_tenant_status(db: Session, tenant_name: str) -> schemas.TenantCheckResponse:
    cleaned_name = tenant_name.strip()
    tenant = db.query(Tenant).filter(
        func.lower(Tenant.tenant_name) == func.lower(cleaned_name)
    ).first()

    if not tenant:
        return schemas.TenantCheckResponse(
            exists=False,
            tenant=None,
            user_count=0,
            property_count=0,
            allow_new_user=True,
            allow_new_property=True
        )

    user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    property_count = db.query(Property).filter(Property.tenant_id == tenant.id).count()

    is_single = (tenant.tenant_type == TenantType.SINGLE)
    allow_new_user = (not is_single) or (user_count == 0)
    allow_new_property = (not is_single) or (property_count == 0)

    return schemas.TenantCheckResponse(
        exists=True,
        tenant=schemas.TenantResponse.model_validate(tenant),
        user_count=user_count,
        property_count=property_count,
        allow_new_user=allow_new_user,
        allow_new_property=allow_new_property
    )

# USERNAME GENERATION & USER CRUD

def _generate_unique_username(db: Session, email: str, full_name: str) -> str:
    """Generates a clean, lowercase username from email or name and guarantees uniqueness."""
    base_raw = email.split("@")[0] if "@" in email else full_name
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", base_raw).lower().strip("_") or "user"

    candidate = cleaned
    counter = 1
    while db.query(User).filter(User.user_name == candidate).first():
        candidate = f"{cleaned}_{counter}"
        counter += 1

    return candidate


def create_user(db: Session, user: schemas.UserCreate) -> User:
    # 1. Verify tenant existence
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified Tenant does not exist."
        )

    # 2. Enforce SINGLE tenant quota (1 user max; GROUP/COMMERCIAL allow unlimited)
    if tenant.tenant_type == TenantType.SINGLE:
        existing_user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
        if existing_user_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quota Exceeded: Tenant '{tenant.tenant_name}' is set to SINGLE and already has an assigned user."
            )

    # 3. Check unique credentials
    if db.query(User).filter(User.email_id == user.email_id.strip()).first():
        raise HTTPException(status_code=400, detail="Email address is already registered.")
    if db.query(User).filter(User.phone_number == user.phone_number.strip()).first():
        raise HTTPException(status_code=400, detail="Phone number is already registered.")

    # 4. Auto-generate user_name internally (UI does not supply it)
    auto_username = (
        user.user_name.strip() 
        if getattr(user, "user_name", None) and user.user_name.strip() 
        else _generate_unique_username(db, user.email_id, user.full_name)
    )

    db_user = User(
        tenant_id=tenant.id,
        user_name=auto_username,
        full_name=user.full_name.strip(),
        phone_number=user.phone_number.strip(),
        role=user.role,
        is_active=user.is_active,
        email_id=user.email_id.strip(),
        password=hash_password(user.password),
        address=user.address,
        dob=user.dob,
        bio_details=user.bio_details,
        created_by=user.created_by,
        updated_by=user.updated_by
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    results = (
        db.query(
            User,
            Tenant.tenant_name,
            Tenant.tenant_type,
            func.coalesce(func.count(distinct(Property.id)), 0).label("property_count")
        )
        .join(Tenant, User.tenant_id == Tenant.id)
        .outerjoin(Property, User.user_name == Property.user_name)
        .group_by(User.id, Tenant.tenant_name, Tenant.tenant_type)
        .order_by(User.created_at.desc())
        .all()
    )

    users_list = []
    for user, t_name, t_type, p_count in results:
        user_data = {column.name: getattr(user, column.name) for column in user.__table__.columns}
        user_data["tenant_name"] = t_name
        user_data["tenant_type"] = t_type.value if hasattr(t_type, "value") else str(t_type)
        user_data["property_count"] = int(p_count or 0)
        users_list.append(user_data)

    return users_list


def get_user(db: Session, user_id: UUID):
    result = (
        db.query(User, Tenant.tenant_name, Tenant.tenant_type)
        .join(Tenant, User.tenant_id == Tenant.id)
        .filter(User.id == user_id)
        .first()
    )
    if not result:
        return None

    user, t_name, t_type = result
    user_data = {column.name: getattr(user, column.name) for column in user.__table__.columns}
    user_data["tenant_name"] = t_name
    user_data["tenant_type"] = t_type.value if hasattr(t_type, "value") else str(t_type)
    return user_data


def update_user(db: Session, user_id: UUID, user_data: schemas.UserCreate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    data = user_data.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        data["password"] = hash_password(data["password"])
    elif "password" in data:
        del data["password"]

    for key, value in data.items():
        if hasattr(user, key) and key != "user_name":  # user_name stays immutable
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    db.delete(user)
    db.commit()
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email_id == email.strip()).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

# PROPERTY CRUD OPERATIONS

def create_property(db: Session, property_data: schemas.PropertyCreate):
    # 1. Resolve user by user_name
    user = db.query(User).filter(User.user_name == property_data.user_name.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{property_data.user_name}' does not exist."
        )

    tenant = user.tenant

    # 2. Enforce SINGLE property quota (1 property max)
    if tenant.tenant_type == TenantType.SINGLE:
        existing_property_count = db.query(Property).filter(Property.tenant_id == tenant.id).count()
        if existing_property_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quota Exceeded: Tenant '{tenant.tenant_name}' is set to SINGLE and can only own 1 property."
            )

    # 3. Check property code uniqueness
    if db.query(Property).filter(Property.property_code == property_data.property_code.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Property code '{property_data.property_code}' already exists."
        )

    # 4. Save property
    prop_dict = property_data.model_dump()
    prop_dict["user_name"] = user.user_name
    prop_dict["property_code"] = prop_dict["property_code"].strip()

    db_property = Property(
        **prop_dict,
        tenant_id=tenant.id
    )

    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def get_properties(db: Session):
    results = (
        db.query(Property, Tenant.tenant_name)
        .join(Tenant, Property.tenant_id == Tenant.id)
        .order_by(Property.created_at.desc())
        .all()
    )

    properties_list = []
    for prop, tenant_name in results:
        prop_data = {column.name: getattr(prop, column.name) for column in prop.__table__.columns}
        prop_data["tenant_name"] = tenant_name or "No Tenant"
        properties_list.append(prop_data)

    return properties_list


def get_property(db: Session, property_id: UUID):
    result = (
        db.query(Property, Tenant.tenant_name)
        .join(Tenant, Property.tenant_id == Tenant.id)
        .filter(Property.id == property_id)
        .first()
    )

    if not result:
        return None

    property_obj, tenant_name = result
    data = {column.name: getattr(property_obj, column.name) for column in property_obj.__table__.columns}
    data["tenant_name"] = tenant_name or "No Tenant"
    return data


def get_properties_by_username(db: Session, user_name: str):
    return db.query(Property).filter(Property.user_name == user_name.strip()).all()


def update_property(db: Session, property_id: UUID, property_data: schemas.PropertyCreate):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        return None

    data = property_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        if hasattr(db_property, key):
            setattr(db_property, key, value)

    db.commit()
    db.refresh(db_property)
    return db_property


def delete_property(db: Session, property_id: UUID) -> bool:
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        return False

    db.delete(db_property)
    db.commit()
    return True

# DOCUMENT OPERATIONS

def create_property_document(db: Session, doc_data: schemas.DocumentCreate) -> models.Document:
    db_doc = models.Document(
        property_code=doc_data.property_code,
        property_address=doc_data.property_address,
        document_type=doc_data.document_type,
        path_url=doc_data.path_url,
        created_by=doc_data.created_by
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def get_documents_by_property_code(db: Session, property_code: str):
    return db.query(models.Document).filter(models.Document.property_code == property_code).all()


def delete_property_document(db: Session, document_id: int) -> bool:
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False

# SUMMARY & AGGREGATION QUERIES

def get_user_property_summary(db: Session, user_name: str):
    user = db.query(User).filter(User.user_name == user_name.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_name}' not found")

    properties = db.query(Property).filter(Property.user_name == user.user_name).all()
    tenant = user.tenant

    return {
        "user_name": user.user_name,
        "tenant_id": tenant.id,
        "tenant_name": tenant.tenant_name,
        "property_count": len(properties),
        "properties": properties
    }


def get_tenant_property_summary(db: Session, tenant_id: UUID):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    properties = db.query(Property).filter(Property.tenant_id == tenant.id).all()
    return {
        "tenant_id": tenant.id,
        "tenant_name": tenant.tenant_name,
        "property_count": len(properties),
        "properties": properties
    }


def get_tenant_summary(db: Session):
    # Subquery 1: count users per tenant
    user_counts_sub = (
        db.query(
            User.tenant_id.label("tenant_id"),
            func.count(User.id).label("user_count")
        )
        .group_by(User.tenant_id)
        .subquery()
    )

    # Subquery 2: count properties per tenant
    # (Checking BOTH Property.tenant_id AND matching via user_name)
    prop_counts_sub = (
        db.query(
            Property.tenant_id.label("tenant_id"),
            func.count(Property.id).label("property_count")
        )
        .group_by(Property.tenant_id)
        .subquery()
    )

    # Main query joining subqueries onto Tenant
    results = (
        db.query(
            Tenant.id.label("tenant_id"),
            Tenant.tenant_name.label("tenant_name"),
            Tenant.tenant_type.label("tenant_type"),
            func.coalesce(user_counts_sub.c.user_count, 0).label("user_count"),
            func.coalesce(prop_counts_sub.c.property_count, 0).label("property_count")
        )
        .outerjoin(user_counts_sub, Tenant.id == user_counts_sub.c.tenant_id)
        .outerjoin(prop_counts_sub, Tenant.id == prop_counts_sub.c.tenant_id)
        .order_by(Tenant.tenant_name.asc())
        .all()
    )

    return [
        {
            "tenant_id": row.tenant_id,
            "tenant_name": row.tenant_name,
            "tenant_type": row.tenant_type.value if hasattr(row.tenant_type, "value") else str(row.tenant_type),
            "user_count": int(row.user_count),
            "property_count": int(row.property_count)
        }
        for row in results
    ]


def get_users_with_property_counts(db: Session):
    results = (
        db.query(
            User.user_name.label("user_name"),
            User.full_name.label("full_name"),
            Tenant.id.label("tenant_id"),
            Tenant.tenant_name.label("tenant_name"),
            func.coalesce(func.count(distinct(Property.id)), 0).label("property_count")
        )
        .join(Tenant, User.tenant_id == Tenant.id)
        .outerjoin(Property, User.user_name == Property.user_name)
        .group_by(User.user_name, User.full_name, Tenant.id, Tenant.tenant_name)
        .all()
    )

    return [
        {
            "user_name": row.user_name,
            "full_name": row.full_name,
            "tenant_id": row.tenant_id,
            "tenant_name": row.tenant_name,
            "property_count": row.property_count
        }
        for row in results
    ]


def get_user_property_counts(db: Session):
    return get_users_with_property_counts(db)