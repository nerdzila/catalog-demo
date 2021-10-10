from typing import Optional

from pydantic import BaseModel


# Different User Schemas for GET (UserOut) and
# PUT/POST (UserIn) endpoints, DELETEd users get their
# own schema
class UserBase(BaseModel):
    """Email and Admin status: always relevant"""
    email: str
    is_admin: bool


class UserIn(UserBase):
    """Password: only relevant when creating/updating"""
    password: str


class UserOut(UserBase):
    """ID: only relevant when retrieving existing users"""
    id: int

    class Config:
        orm_mode = True


class UserDeleted(BaseModel):
    """For deleted users we return only the ID"""
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
