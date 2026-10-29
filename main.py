from fastapi import FastAPI, Depends, HTTPException
from schema import ProductCreate, ProductResponse, SignUp, Login, ForgetPassword, ResetPassword, CartItem, CartItem, CartResponse, CheckoutAddress
from fastapi.security import OAuth2PasswordRequestForm
from model import Product, User, UserRole, Cart, Order
from database import get_db, Base, engine
from sqlalchemy.orm import Session
from utils import hash_password, verify_password
from auth import create_access_token, decode_token, get_current_user
from paystack import initialize_payment

app = FastAPI()

@app.post("/signup")
def register(request: SignUp, db: Session = Depends(get_db)):
    if db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Email or username already exist"

        )

    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=401,
            detail="Password does not match"
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

@app.get("/admin/dashboard")
def get_admin_dashboad(user: User=Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are Forbidden to enter this page!"
        )
  
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
def get_product_byId(Product_id: int, db: Session = Depends(get_db)): 
    get_product = db.query(Product).filter(Product.id == Product_id).all()
    return get_product

@app.get("/Product/{name}", response_model=ProductResponse)
def get_product_byName(Product_name: str, db: Session=Depends(get_db)): 
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
    if not update_product_by_id:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
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

@app.delete("/product/{product_id}", response_model=ProductResponse)
def delete_product(product_id: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,            
            detail="Not Authorized"
        )
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="product not found"
        )
    

 
    db.delete(product)
    db.commit()
    return product

@app.post("/cart")
def add_to_cart(request: CartItem, currentuser: User=Depends(get_current_user), db: Session=Depends(get_db)):
    product = db.query(Product).filter(Product.id == request.product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    if product.stock < request.qty:
        raise HTTPException(
            status_code=400,
            detail=f"The available product in stock for purchase is {product.stock}"
        )

    existing_cart = db.query(Cart).filter(Cart.user_id == currentuser.userId, Cart.product_id == request.product_id).first()

    if existing_cart:
        new_quantity = existing_cart.quantity + request.qty #is this supposed to be existing_cart

        if product.stock < new_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"The available product in stock for purchase is {product.stock}"
            )

        existing_cart.quantity = new_quantity
        db.commit()
        db.refresh(existing_cart)

        return existing_cart

    cart_item = Cart(
        user_id=currentuser.userId,
        product_id=request.product_id,
        quantity = request.qty
        
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item

@app.get("/cart", response_model=list[CartResponse])
def get_user_cart(currentuser: User=Depends(get_current_user), db: Session=Depends(get_db)):
    user_cart = db.query(Cart).filter(Cart.user_id == currentuser.userId).all()
    if not user_cart:
        raise HTTPException(    
            status_code=404,
            detail="Cart not found"
        )

    return [
        {
        "id": cart.id,
        "user_id": cart.user_id,
        "product_id": cart.product_id,
        "quantity": cart.quantity,
        "product_name": cart.product.name,
        "product_price": cart.product.price,
        "created_at": cart.created_at
        }
    for cart in user_cart
    ]

@app.get("/carts")
def get_all_cart(currentuser: User=Depends(get_current_user), db: Session=Depends(get_db)):
 
    if currentuser.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="you are forbidden to access this page"
        )
    carts = db.query(Cart).all()
    return carts

@app.delete("/cart/product/{product_id}")
def delete_cart(product_id: int, currentuser: User=Depends(get_current_user), db: Session=Depends(get_db)):
    cart = db.query(Cart).filter(Cart.product_id == product_id, Cart.user_id == currentuser.userId).first()
    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )
    db.delete(cart)
    db.commit()

    return cart

@app.delete("/cart")
def delete_all_cart(currentuser: User=Depends(get_current_user), db:Session=Depends(get_db)):
    user_cart = db.query(Cart).filter(Cart.user_id == currentuser.userId).first()

    if not user_cart:
        raise HTTPException(
            status_code=404,
            detail="No cart available"
        )

    db.delete(user_cart)
    db.commit()

    return user_cart 


@app.put("/cart")
def edit_cart(id: int, cart: CartItem, cartcurrentuser: User=Depends(get_current_user), db: Session=Depends(get_db)):
    edit_c = db.query(Cart).filter(Cart.id ==id, Cart.user_id == cartcurrentuser.userId).first()

    if not edit_c:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"  
        )

    edit_c.quantity = cart.qty

    db.commit()
    db.refresh(edit_c)

    return edit_c


@app.post("/order")
async def checkout(request: CheckoutAddress, currentuser: User=Depends (get_current_user), db: Session=Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == currentuser.userId).all()

    if not cart:
        raise HTTPException( 
            status_code=404,
            detail="cart is empty"
        )
    total_amount = 0
    cart_product = []

    for item in cart:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException (
                status_code=404,
                detail="product not found"
                )

        
        item_total=product.price * item.quantity
        total_amount +=item_total

        cart_product.append({
            "cart_item": item,
            "product": product,
            "item_total": item_total
        })

    payment = await initialize_payment(
        email=currentuser.email,
        amount=total_amount
    )

    payment_data = payment["data"]

    for data in cart_product:
        item = data["cart_item"]

        order = Order(
            user_id = currentuser.userId,
            product_id = item.product_id,
            quantity = item.quantity,
            cart_id = item.id,
            amount=data["item_total"],
            reference = payment_data["reference"],
            shipping_address = request.model_dump()
        )

        db.add(order)

    db.commit()

    return {
        "message": "Payment Initialized successful",
        "authorization_url": payment_data["authorization_url"],
        "payment_reference": payment_data["reference"],
        "total_amount": total_amount
        }
    


    







