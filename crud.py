from models import User, Tenant
from fastapi import HTTPException

# TENANT CRUD OPERATIONS

def create_tenant(db, tenant):
    db_tenant = Tenant(**tenant.model_dump())

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    return db_tenant


def get_tenants(db):
    return db.query(Tenant).all()


def get_tenant(db, tenant_id):
    return db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()


def update_tenant(db, tenant_id, tenant_data):
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if not tenant:
        return None

    for key, value in tenant_data.model_dump().items():
        setattr(tenant, key, value)

    db.commit()
    db.refresh(tenant)

    return tenant


def delete_tenant(db, tenant_id):
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if not tenant:
        return None

    db.delete(tenant)
    db.commit()

    return tenant

# USER CRUD OPERATIONS

def create_user(db, user):
    tenant = None

# case 1: Both tenant_id and tenant_name are provided
    if user.tenant_id and user.tenant_name:

        tenant = db.query(Tenant).filter(
            Tenant.id == user.tenant_id,
            Tenant.tenant_name == user.tenant_name
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant ID not found."
            )
        
        if tenant.tenant_name != user.tenant_name:
            raise HTTPException(
                status_code=400,
                detail="Tenant ID and name do not match."
            )
        
        # case 2 : Only tenant_id is provided
    elif user.tenant_id:

        tenant = db.query(Tenant).filter(
            Tenant.id == user.tenant_id
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant ID not found."
            )
        
        # case 3 : Only tenant_name is provided
    elif user.tenant_name:

        tenant = db.query(Tenant).filter(
            Tenant.tenant_name == user.tenant_name
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant name not found."
            )
        
        #case 4 : Neither tenant_id nor tenant_name is provided
    else:
        raise HTTPException(
            status_code=400,
            detail="Either tenant_id or tenant_name must be provided."
        )

    db_user = User(
    phone_number=user.phone_number,
    role=user.role,
    full_name=user.full_name,

    tenant_id=tenant.id,      # Automatically assigned
    tenant_name=tenant.tenant_name,  # Automatically assigned

    is_active=user.is_active,
    email_id=user.email_id,
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


def get_users(db):
    return db.query(User).all()


def get_user(db, user_id):
    return db.query(User).filter(
        User.id == user_id
    ).first()


def update_user(db, user_id, user_data):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return None

    for key, value in user_data.model_dump().items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db, user_id):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user