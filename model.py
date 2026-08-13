from sqlalchemy import String, Float, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
import uuid

class User(Base):
    __tablename__="username"

    userId: Mapped[str] = mapped_column(String, primary_key=True, unique=True, default=lambda : str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, primary_key=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    


class Product(Base):
    __tablename__="product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)
    description = Column(String, nullable=False)