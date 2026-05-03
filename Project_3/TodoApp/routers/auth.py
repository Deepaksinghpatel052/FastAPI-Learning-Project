from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from ..models import Users
from passlib.context import CryptContext
from ..Database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt


router = APIRouter(
    prefix="/auth",
    tags = ["auth"]

)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = "5e67df1e27ff6c8d3a8d9553a45302008384a45b4e6317868081eed7d47c44a3"
ALGORITHEM = "HS256"


class UserRequest(BaseModel):
    email: str = Field(min_length=5)
    username: str = Field(min_length=5)
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    password: str = Field(min_length=2)
    role: str = Field(min_length=2)


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[session, Depends(get_db)]

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    create_user_model = Users(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        heshed_password = bcrypt_context.hash(user_request.password),
        is_active = True,
        role = user_request.role

    )
    db.add(create_user_model)
    db.commit()


def authonticate_user(username, password, db):
    user_model = db.query(Users).filter(Users.username == username).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password, user_model.heshed_password):
        return False
    return user_model


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHEM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHEM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: int = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"username": username, "id":user_id, "user_role": user_role}
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/token", response_model=Token)
async def get_user_token(user_request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
                         db: db_dependency):
    user_authonticat = authonticate_user(user_request_form.username, user_request_form.password, db)
    if not user_authonticat:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    
    token = create_access_token(user_authonticat.username, user_authonticat.id, user_authonticat.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
    


