from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

from . import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",
                                              auto_error=False)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY,
                             algorithm=config.ALGORITHM)
    return encoded_jwt


def get_email_from_token(token: str):
    payload = jwt.decode(token, config.SECRET_KEY,
                         algorithms=[config.ALGORITHM])
    email: str = payload.get("sub")
    return email
