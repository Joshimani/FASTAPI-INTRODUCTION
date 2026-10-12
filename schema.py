from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class SignUp(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str
    confirm_password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class ForgetPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    description: str

class ProductResponse(ProductCreate):
    id: int

class CartItem(BaseModel):
    product_id: int
    qty: int

class CartResponse(BaseModel):
    product_name: str
    product_id: int
    id: int
    quantity: int
    user_id: str
    product_price: float
    created_at:datetime


class CheckoutAddress(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    country: str
    postal_code: str


