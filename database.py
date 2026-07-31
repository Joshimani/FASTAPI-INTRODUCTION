from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

Database = os.getenv("DATABASE_URL")
engine = create_engine(Database)

session = sessionmaker(
    autoflush=False,
    autocommit = False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db=session()
    try: 
        yield db
    finally:
        db.close()