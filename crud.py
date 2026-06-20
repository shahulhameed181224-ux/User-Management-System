from models import User


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


def delete_user(db, user_id):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user:
        db.delete(user)
        db.commit()

    return user

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