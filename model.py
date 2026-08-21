from sqlalchemy import String, Float, Integer, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import uuid
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__="user"

    userId: Mapped[str] = mapped_column(String, primary_key=True, unique=True, default=lambda : str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, default=lambda : str("user"))
    email = Column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    cart = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    


class Product(Base):
    __tablename__="product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    cart_items = relationship("CartItem", back_populates="product")

class Cart(Base):
    __tablename__="cart"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user.userId"), nullable=False, unique=True)
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
  

class CartItem(Base):
    __tablename__ = "cart_item"
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product",back_populates="cart_items")






