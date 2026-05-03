from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos, Users
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from ..Database import SessionLocal
from sqlalchemy.orm import session
from typing import Annotated
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags = ["user"]
    )

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")




class UserInfo(BaseModel):
    id: int = Field(default="id")
    email: str = Field(default="Email")
    username: str = Field(default="username")
    first_name: str = Field(default="First Name")
    last_name: str = Field(default="Last name")
    is_active: bool = Field(default=True)
    role: str = Field(default="User Role")



@router.get("/", status_code=status.HTTP_200_OK, response_model=UserInfo)
async def get_user(current_user: user_dependency, db: db_dependency):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authonticate")
    user_info = db.query(Users).filter(Users.id==current_user.get("id")).first()
    return {"id":user_info.id, "email":user_info.email, 
            "username":user_info.username, "first_name":user_info.first_name, 
            "last_name":user_info.last_name, "is_active":user_info.is_active,
            "role":user_info.role}

class passwordVarification(BaseModel):
    current_password: str = Field(min_length=1, max_length=20)
    new_password: str = Field(min_length=1, max_length=20)



@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(current_user: user_dependency, db: db_dependency, password_varification: passwordVarification):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authonticate")
    user_info = db.query(Users).filter(Users.id==current_user.get("id")).first()
    if not bcrypt_context.verify(password_varification.current_password, user_info.heshed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password changed")
    user_info.heshed_password = bcrypt_context.hash(password_varification.new_password)
    db.add(user_info)
    db.commit()