from sqlalchemy import String, Float, Integer, Column
from database import Base

class Product(Base):
    __tablename__="product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)
    description = Column(String, nullable=False)