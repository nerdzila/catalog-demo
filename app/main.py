from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal, initialize_db


# TODO: delegate DB initalization to migrations library
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

initialize_db()


# ==================
# Dependencies
# ==================
def get_db():  # pragma: no cover
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================
# Endpoints
# ==================
@app.get("/")
def read_root():
    """Root endpoint, for now just says hello to the world"""
    return {"Hello": "World"}


@app.get("/users/", response_model=List[schemas.UserOut])
def read_users(db: Session = Depends(get_db)):
    """Retrieve all users"""
    return crud.get_all_users(db)


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve single user by ID"""
    db_user = crud.get_user(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.post("/users/", response_model=schemas.UserOut)
def create_user(user_in: schemas.UserIn, db: Session = Depends(get_db),):
    """Create a new user"""
    existing_user = crud.get_user_by_email(db, user_in.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = crud.create_user(db, user_in)
    return user


@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_in: schemas.UserIn,
    db: Session = Depends(get_db)
):
    user_db = crud.get_user(db, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    user = crud.update_user(db, user_db, user_in)
    return user
