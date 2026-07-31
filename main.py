from fastapi import FastAPI, Depends
from schema import ProductCreate, ProductResponse
from model import Product
from database import get_db, Base, engine
from sqlalchemy.orm import Session

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/product/{id}", response_model=list[ProductResponse])
def get_product_byId(Product_id= int, db: Session = Depends(get_db)):
    get_product = db.query(Product).filter(Product.id == Product_id).all()
    return get_product

@app.get("/Product/{name}", response_model=ProductResponse)
def get_product_byName(Product_name = str, db: Session=Depends(get_db)):
    get_product_by_name = db.query(Product).filter(Product.name == Product_name).first()
    return get_product_by_name

@app.get("/products", response_model=list[ProductResponse])
def get_product(db: Session = Depends(get_db)):
    get_all_product = db.query(Product).all()
    return get_all_product


@app.post("/product", response_model=ProductResponse)
def create_product( product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product






