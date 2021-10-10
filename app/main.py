from typing import List
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from . import models, crud, schemas, security, config
from .database import SessionLocal, initialize_db


app = FastAPI()

initialize_db()


# ==================================================================
# Dependencies
# ==================================================================
def get_db():  # pragma: no cover
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(security.oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = security.get_email_from_token(token)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


# ==================================================================
# General Purpose Endpoints
# ==================================================================
@app.get("/")
def hello_world():
    """Root endpoint, for now just says hello to the world"""
    return {"Hello": "World"}


@app.post("/token", response_model=schemas.Token)
def login_and_get_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Get auth token from FormData credentials"""
    user = crud.authenticate_user(db, form_data.username,
                                  form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================================================================
# User-related endpoints
# ==================================================================
@app.get("/users/", response_model=List[schemas.UserOut])
def get_user_list(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    """Retrieve all users"""
    return crud.get_all_users(db)


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    """Retrieve single user by ID"""
    db_user = crud.get_user(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.post("/users/", response_model=schemas.UserOut)
def create_user(
    user_in: schemas.UserIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    """Create a new user from JSON payload"""
    existing_user = crud.get_user_by_email(db, user_in.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = crud.create_user(db, user_in)
    return user


@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_in: schemas.UserIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    """Update an existing user from a JSON payload"""
    user_db = crud.get_user(db, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    user = crud.update_user(db, user_db, user_in)
    return user


@app.delete("/users/{user_id}", response_model=schemas.UserDeleted)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    """Delete user with the given ID"""
    user_db = crud.get_user(db, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    crud.delete_user(db, user_db)

    return {"id": user_id}


# ==================================================================
# Product-related endpoints
# ==================================================================
@app.get("/products/", response_model=List[schemas.ProductOut])
def get_product_list(
    db: Session = Depends(get_db),
):
    """Retrieve all products"""
    return crud.get_all_products(db)


@app.get("/products/{product_id}", response_model=schemas.ProductOutDetails)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single product by ID"""
    db_product = crud.get_single_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
