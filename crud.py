from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
import models
import schemas
from models import User, Property
from security import hash_password, verify_password

# ==========================================
# DOCUMENT CRUD OPERATIONS
# ==========================================

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

def delete_property_document(db: Session, document_id: int):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


# ==========================================
# USER CRUD OPERATIONS
# ==========================================

def create_user(db: Session, user: schemas.UserCreate):
    db_user = User(
        phone_number=user.phone_number,
        role=user.role,
        full_name=user.full_name,
        is_active=user.is_active,
        email_id=user.email_id,
        password=hash_password(user.password),
        address=user.address,
        dob=user.dob,
        bio_details=user.bio_details,
        tenant_id=user.tenant_id,
        tenant_name=user.tenant_name,
        tenant_type=user.tenant_type,
        tenant_created_by=user.tenant_created_by,
        tenant_updated_by=user.tenant_updated_by,
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
            func.count(Property.id).label("property_count")
        )
        .outerjoin(
            Property,
            Property.user_id == User.id
        )
        .group_by(User.id)
        .all()
    )

    users = []
    for user, property_count in results:
        user_data = {
            "id": user.id,
            "phone_number": user.phone_number,
            "role": user.role,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "email_id": user.email_id,
            "address": user.address,
            "dob": user.dob,
            "bio_details": user.bio_details,
            "tenant_id": user.tenant_id,
            "tenant_name": user.tenant_name,
            "tenant_type": user.tenant_type,
            "tenant_created_by": user.tenant_created_by,
            "tenant_updated_by": user.tenant_updated_by,
            "created_by": user.created_by,
            "updated_by": user.updated_by,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "property_count": property_count
        }
        users.append(user_data)

    return users

def get_user(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id, user_data: schemas.UserCreate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    data = user_data.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        data["password"] = hash_password(data["password"])
    elif "password" in data:
        del data["password"]

    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    db.delete(user)
    db.commit()
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email_id == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


# ==========================================
# PROPERTY CRUD OPERATIONS
# ==========================================

def create_property(db: Session, property_data: schemas.PropertyCreate):
    user = db.query(User).filter(User.id == property_data.user_id).first()

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Assigned user not found"
        )

    tenant_id = property_data.tenant_id or user.tenant_id
    if tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Assigned user does not belong to a valid tenant"
        )

    db_property = Property(
        user_id=user.id,
        tenant_id=tenant_id,
        property_code=property_data.property_code,
        property_name=property_data.property_name,
        property_location=property_data.property_location,
        property_landmark=property_data.property_landmark,
        latitude=property_data.latitude,
        longitude=property_data.longitude,
        area_size=property_data.area_size,
        measurement_type=property_data.measurement_type,
        plot_type=property_data.plot_type,
        ownership_type=property_data.ownership_type,
        purchase_date=property_data.purchase_date,
        market_value=property_data.market_value,
        description=property_data.description,
        verified_status=property_data.verified_status,
        risk_level=property_data.risk_level,
        fence_status=property_data.fence_status,
        is_active=property_data.is_active,
        last_visited_at=property_data.last_visited_at,
        remarks=property_data.remarks,
        visit_plan=property_data.visit_plan,
        photo_url=property_data.photo_url,
        location_url=property_data.location_url,
        embedded_url=property_data.embedded_url,
        boundary_stones=property_data.boundary_stones,
        encroachment=property_data.encroachment,
        legal_disputes=property_data.legal_disputes,
        neighbour_issues=property_data.neighbour_issues,
        vegetation_issues=property_data.vegetation_issues,
        has_layout_plan=property_data.has_layout_plan,
        has_patta_chitta=property_data.has_patta_chitta,
        latest_ec_date=property_data.latest_ec_date,
        service_required=property_data.service_required,
        additional_notes=property_data.additional_notes,
        land_owner_name=property_data.land_owner_name,
        source=property_data.source,
        created_by=property_data.created_by,
        updated_by=property_data.updated_by
    )

    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def get_properties(db: Session):
    results = (
        db.query(
            models.Property,
            models.User.full_name.label("user_name"),
            models.User.tenant_name.label("tenant_name")
        )
        .outerjoin(models.User, models.Property.user_id == models.User.id)
        .all()
    )

    properties_list = []
    for prop, user_name, tenant_name in results:
        # Dynamically dump all database columns so Pydantic schema never fails
        prop_data = {column.name: getattr(prop, column.name) for column in prop.__table__.columns}
        prop_data["user_name"] = user_name or "No User"
        prop_data["tenant_name"] = tenant_name or "No Tenant"
        properties_list.append(prop_data)

    return properties_list

def get_property(db: Session, property_id):
    result = (
        db.query(
            models.Property,
            models.User.full_name.label("user_name"),
            models.User.tenant_name.label("tenant_name")
        )
        .outerjoin(models.User, models.Property.user_id == models.User.id)
        .filter(models.Property.id == property_id)
        .first()
    )

    if not result:
        return None

    property_obj, user_name, tenant_name = result
    data = {column.name: getattr(property_obj, column.name) for column in property_obj.__table__.columns}
    data["user_name"] = user_name or "No User"
    data["tenant_name"] = tenant_name or "No Tenant"
    return data

def update_property(db: Session, property_id, property_data: schemas.PropertyCreate):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        return None

    for key, value in property_data.model_dump(exclude_unset=True).items():
        if hasattr(db_property, key):
            setattr(db_property, key, value)

    db.commit()
    db.refresh(db_property)
    return db_property

def delete_property(db: Session, property_id):
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if db_property is None:
        return None

    db.delete(db_property)
    db.commit()
    return True


# ==========================================
# SUMMARY & AGGREGATION QUERIES
# ==========================================

def get_user_property_summary(db: Session, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    properties = db.query(Property).filter(Property.user_id == user_id).all()
    return {
        "user_id": user.id,
        "user_name": user.full_name,
        "tenant_id": user.tenant_id,
        "tenant_name": user.tenant_name,
        "tenant_type": user.tenant_type,
        "property_count": len(properties),
        "properties": properties
    }

def get_tenant_property_summary(db: Session, tenant_id):
    users = db.query(User).filter(User.tenant_id == tenant_id).all()
    if not users:
        raise HTTPException(status_code=404, detail="Tenant not found")

    user_ids = [user.id for user in users]
    properties = db.query(Property).filter(Property.user_id.in_(user_ids)).all()

    return {
        "tenant_id": tenant_id,
        "tenant_name": users[0].tenant_name,
        "tenant_type": users[0].tenant_type,
        "property_count": len(properties),
        "properties": properties
    }

def get_tenant_users(db: Session, tenant_id):
    users = db.query(User).filter(User.tenant_id == tenant_id).all()
    if not users:
        raise HTTPException(status_code=404, detail="Tenant not found or has no users")

    return {
        "tenant_id": tenant_id,
        "tenant_name": users[0].tenant_name,
        "user_count": len(users),
        "users": users
    }

def get_tenant_summary(db: Session):
    results = (
        db.query(
            User.tenant_id.label("tenant_id"),
            User.tenant_name.label("tenant_name"),
            func.count(distinct(User.id)).label("user_count"),
            func.count(distinct(Property.id)).label("property_count")
        )
        .outerjoin(Property, Property.user_id == User.id)
        .filter(User.tenant_id.isnot(None))
        .group_by(User.tenant_id, User.tenant_name)
        .all()
    )

    return [
        {
            "tenant_id": row.tenant_id,
            "tenant_name": row.tenant_name,
            "user_count": row.user_count,
            "property_count": row.property_count
        }
        for row in results
    ]

def get_users_with_property_counts(db: Session):
    results = (
        db.query(
            User.id.label("user_id"),
            User.full_name.label("user_name"),
            User.tenant_id.label("tenant_id"),
            User.tenant_name.label("tenant_name"),
            func.count(Property.id).label("property_count")
        )
        .outerjoin(Property, Property.user_id == User.id)
        .group_by(User.id, User.full_name, User.tenant_id, User.tenant_name)
        .all()
    )

    return [
        {
            "user_id": str(row.user_id),
            "user_name": row.user_name,
            "tenant_id": str(row.tenant_id) if row.tenant_id else None,
            "tenant_name": row.tenant_name,
            "property_count": row.property_count
        }
        for row in results
    ]

def get_user_property_counts(db: Session):
    return get_users_with_property_counts(db)