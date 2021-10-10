from decimal import Decimal

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
# ==================================================================
class UserBase(BaseModel):
    """Properties that most user schemas use"""
    email: str
    is_admin: bool


class UserIn(UserBase):
    """The password is only relevant for PUT/POST requests"""
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
class ProductBase(BaseModel):
    """Commonly used properties"""
    sku: str
    name: str
    price: Decimal
    brand: str


class ProductIn(ProductBase):
    """POST/PUT endpoints should have all non-ID props"""
    description: str


class ProductOut(ProductBase):
    """When retrieving a list of products, add the ID"""
    id: int

    class Config:
        orm_mode = True


class ProductOutDetails(ProductOut):
    """When looking at a product detail, add the description"""
    description: str


class ProductDeleted(BaseModel):
    """DELETE endpoint gets only the ID"""
    id: int
