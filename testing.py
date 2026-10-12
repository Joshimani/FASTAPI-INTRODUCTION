import jwt
import os
from datetime import timezone, datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends 
from sqlalchemy.orm import Session 
from dotenv import load_dotenv
from model import User
from database import get_db

load_dotenv()

OAuth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
secrete_key = os.getenv("SECRET_KEY")
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
        secrete_key,
        algorithm=algorithm
    )
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            secrete_key,
            algorithms=[algorithm]
        )

        userId: str=payload.get("sub")
        if not userId:
            raise HTTPException(
                status_code=404,
                detail="user Id not found"
            )
        return userId
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="token expired"
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

def get_current_user(token: str=Depends(OAuth2_scheme), db: Session=Depends(get_db)) -> User:
    userId = decode_token(token)
    user = db.query(User).filter(User.userId==userId).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )
    return user