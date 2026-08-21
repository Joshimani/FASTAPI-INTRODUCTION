from pydantic import BaseModel, ConfigDict, EmailStr

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
    qty: int
    description: str

class ProductResponse(ProductCreate):
    id: int
