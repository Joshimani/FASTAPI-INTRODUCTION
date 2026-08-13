import jwt 
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv("SECRET_KEY") 
algorithm = os.getenv("ALGORITHM")
EXPIRE_MIN = 30


def create_access_token(userId: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    payload = {
        "sub": userId,
        "exp": expire
    }
    
    token = jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
        
    )

    return token
