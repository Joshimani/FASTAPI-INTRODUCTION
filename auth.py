import jwt 
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from model import User



load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

secret_key = os.getenv("SECRET_KEY") 
algorithm = os.getenv("ALGORITHM", "HS256")
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


def decode_token(token: str):
    try:
        payload=jwt.decode( 
            token,
            secret_key,
            algorithms=[algorithm]
        )

        userId: str=payload.get("sub")
        if not userId:
            raise HTTPException(
                status_code=401,
                detail="Invalid user ID"
            )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
                                         
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

    return userId
        

def get_current_user(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)) -> User:
    userId=decode_token(token)

    user = db.query(User).filter(User.userId == userId).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )
    return user