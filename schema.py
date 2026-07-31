from pydantic import BaseModel, ConfigDict
class ProductCreate(BaseModel):
    name: str
    price: float
    qty: int
    description: str

class ProductResponse(ProductCreate):
    id: int