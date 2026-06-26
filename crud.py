from models import User, Tenant

# USER CRUD OPERATIONS

def create_user(db, user):
    db_user = User(**user.model_dump())

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