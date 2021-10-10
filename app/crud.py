from typing import Optional, List

from sqlalchemy.orm import Session

from . import models, schemas, security


# ==================================================================
# User CRUD utilities
# ==================================================================
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserIn) -> models.User:
    new_user = models.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        is_admin=user_in.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(
    db: Session,
    user_db: models.User,
    user_in: schemas.UserIn
) -> models.User:
    fields_to_update = user_in.dict(exclude_unset=True)

    if "password" in fields_to_update:
        user_db.hashed_password = security.get_password_hash(
            fields_to_update["password"]
        )
        del fields_to_update["password"]

    for field, value in fields_to_update.items():
        setattr(user_db, field, value)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


def delete_user(db: Session, user_db: models.User):
    db.delete(user_db)
    db.commit()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user


# ==================================================================
# Product CRUD utilities
# ==================================================================
def get_all_products(db: Session) -> List[models.Product]:
    return db.query(models.Product).all()
