from pydantic import BaseModel


# ==================================================================
# General purpose schemas
# ==================================================================
class Token(BaseModel):
    """Schema to return JWT token"""
    access_token: str
    token_type: str


# ==================================================================
# User Schemas
#
# Different User Schemas for GET (UserOut) and
# PUT/POST (UserIn) endpoints, DELETEd users get their
# own schema
# ==================================================================
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

# ==================================================================
# Product Schemas
# ==================================================================
