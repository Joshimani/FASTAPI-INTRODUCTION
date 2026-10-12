from sqlalchemy import String, Float, Integer, Column, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import uuid
from enum import Enum
from datetime import datetime, timezone

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class OrderStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__="user"

    userId: Mapped[str] = mapped_column(String, primary_key=True, unique=True, default=lambda : str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, default=lambda : str("admin"))
    email = Column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    cart = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    


class Product(Base):
    __tablename__="product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    cart_items = relationship("Cart", back_populates="product")
    order = relationship("Order", back_populates="product")

class Cart(Base):
    __tablename__="cart"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user.userId"), nullable=False)
    user = relationship("User", back_populates="cart")
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product",back_populates="cart_items")
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    order = relationship("Order", back_populates="cart")

class Order(Base):
    __tablename__="order"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("user.userId"))
    product_id = Column(Integer, ForeignKey("product.id"))
    quantity = Column(Integer, nullable=False)
    cart_id = Column(Integer, ForeignKey("cart.id"))
    reference = Column(String, nullable=False, default=lambda: str(uuid.uuid4()))
    status = Column(String, default=lambda: str("pending"))
    amount= Column(Float, nullable=False)
    cart = relationship("Cart", back_populates="order")
    product = relationship("Product", back_populates="order")
    currency = Column(String, default="NGN", nullable=False)
    shipping_address = Column(JSON, nullable=False)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    






