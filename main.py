from fastapi import FastAPI, Depends, HTTPException
from schema import ProductCreate, ProductResponse, SignUp, Login, ForgetPassword, ResetPassword
from fastapi.security import OAuth2PasswordRequestForm
from model import Product, User, UserRole
from database import get_db, Base, engine
from sqlalchemy.orm import Session
from utils import hash_password, verify_password
from auth import create_access_token, decode_token, get_current_user

app = FastAPI()

@app.post("/signup")
def register(request: SignUp, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        return HTTPException(
            status_code=409,
            detail="Email already exist"

        )
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=401,
            detail="Password do no match"

        )
    password = hash_password(request.password)

    user =User(
        full_name=request.full_name,
        username = request.username,
        email = request.email,
        password=password

    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Successfully created an account",
        "id": user.userId 
    }

@app.post("/token")
def get_authorize(request: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(User).filter(User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found!"
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect passwordor email"
        )
    create_token= create_access_token(
        user.userId
    )

    return {
        "access_token": create_token,
        "token_type": "bearer"
    }

@app.post("/login")
def login(request: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found!"
        )
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=401, 
            detail="Incorrect email or password"
        )

    create_token = create_access_token(
        user.userId
    )

    return {
        "message": "Login Sucessful",
        "token": create_token,

        }

@app.get("/me")
def get_user(user: User= Depends(get_current_user)):
    

    return {
        "userId":user.userId,
        "name": user.full_name,
        "email": user.email,
        "role": user.role

    }



@app.post("/forgetpassword")
def forget_password(request: ForgetPassword, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.email== request.email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found!"
        )
    create_token = create_access_token(
        user.userId
    )
    return {
        "toekn":create_token
    }

@app.post("/resetpassword")
def reset_password(request: ResetPassword, db: Session = Depends(get_db)):
    userId = decode_token(request.token)
    user = db.query(User).filter(User.userId == userId).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found!"
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Password do not match"
        )
    password = hash_password(request.new_password)
    user.password = password

    db.commit()
    db.refresh(user)

    return {
        "message": "Password reset successful"
    }
                    
@app.get("/product/{id}", response_model=list[ProductResponse])
def get_product_byId(Product_id= int, db: Session = Depends(get_db)):
    get_product = db.query(Product).filter(Product.id == Product_id).all()
    return get_product

@app.get("/Product/{name}", response_model=ProductResponse)
def get_product_byName(Product_name = str, db: Session=Depends(get_db)):
    get_product_by_name = db.query(Product).filter(Product.name == Product_name).first()
    return get_product_by_name

@app.put("/product/{product_id}", response_model=ProductResponse)
def product_update(
    product_id: int,
    product: ProductCreate, user: User=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Not Authorized"
            )
    update_product_by_id = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    update_product_by_id.name = product.name
    update_product_by_id.price = product.price

    db.commit()
    db.refresh(update_product_by_id)

    return update_product_by_id

@app.get("/products", response_model=list[ProductResponse])
def get_product(db: Session = Depends(get_db)):
    get_all_product = db.query(Product).all()
    return get_all_product


@app.post("/product", response_model=ProductResponse)
def create_product(product: ProductCreate, user: User=Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Not Authorized"
        )
    
    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@app.delete("/product{product_id}", response_model=ProductResponse)
def delete_product(product_id=int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    delete = db.query(Product).filter(Product.id == product_id).first()

    if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Not Authorized"
            )
    db.delete(delete)
    db.commit()
    return delete







