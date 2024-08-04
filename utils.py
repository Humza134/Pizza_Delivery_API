
from typing import Union
from passlib.context import CryptContext
from dotenv import load_dotenv, find_dotenv
import os
from datetime import timedelta,timezone,datetime
from jose import jwt,JWTError

# Load environment variables from .env file
load_dotenv()

# Accessing environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")

# password hashing
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_refresh_token(data:dict, expires_delta:Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm = str(ALGORITHM))
    return encoded_jwt

def validate_refresh_token(refresh_token: str)-> int | None:
    try:
        payload = jwt.decode(refresh_token, str(SECRET_KEY), algorithms=str(ALGORITHM))
        user_id: int | None = payload.get("id")
        if not user_id:
            return None
        return user_id
    
    except JWTError:
        return None


