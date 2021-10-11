from sqlalchemy import (
    Boolean, Column, Integer, String, Numeric,
    DateTime, ForeignKey
)
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Numeric)
    brand = Column(String)
    description = Column(String)


class ProductHit(Base):
    __tablename__ = "product_hits"

    id = Column(Integer, primary_key=True, index=True)
    seen_at = Column(DateTime, default=func.now())
    product_id = Column(Integer, ForeignKey('products.id'))
