from typing import Annotated, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, engine
from model import User
from schemas import SignUpModel, TokenData
from utils import get_password_hash, verify_password, create_refresh_token
from dotenv import load_dotenv, find_dotenv
import os
from datetime import timedelta, timezone, datetime
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# Load environment variables from .env file
load_dotenv()

# Accessing environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")

# Define the FastAPI app
app = FastAPI()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Example route to test the API
@auth_router.get("/")
async def hello():
    return {"message": "Hello World"}

@auth_router.post("/signup")
async def signup(user: SignUpModel, db: Annotated[Session, Depends(get_db)]):
    db_email = db.query(User).filter(User.email == user.email).one_or_none()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    
    db_username = db.query(User).filter(User.username == user.username).one_or_none()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this username already exists")
    
    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_staff=user.is_staff,
        is_active=user.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

class InvalidUserException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

def get_user(db: Session, username: Union[str, None] = None):
    try:
        if username is None:
            raise InvalidUserException(status_code=400, detail="Username is required")
        user = db.query(User).filter(User.username == username).one_or_none()
        if not user:
            raise InvalidUserException(status_code=404, detail="User not found")
        return user
    except InvalidUserException:
        raise
    except Exception as e:
        raise InvalidUserException(status_code=500, detail=str(e))
    
def authenticate_user(db, username: str, password: str):
    try:
        user = get_user(db, username)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user
    except InvalidUserException:
        raise

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))

    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth_scheme)], db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[str(ALGORITHM)])
        print("Payload:", payload)  # Debugging line
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    print("User:", user)  # Debugging line
    return user

# Login user
@auth_router.post("/login")
async def service_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
        )

        # Generate refresh token (you might want to set a longer expiry for this)
        refresh_token_expires = timedelta(minutes=float(REFRESH_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_refresh_token(
            data={"sub": user.username, "id": user.id}, expires_delta=refresh_token_expires)

        return {"access_token": access_token, "token_type": "bearer", "user": user, "expires_in": int(access_token_expires.total_seconds()), "refresh_token": refresh_token}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect access or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@auth_router.get("/user/me")
async def get_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

# Include the auth router in the main app
app.include_router(auth_router)
