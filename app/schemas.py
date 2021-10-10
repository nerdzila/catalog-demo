from pydantic import BaseModel


# Different User Schemas for GET (UserOut) and
# PUT/POST (UserIn) endpoints
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
