from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos
from pydantic import BaseModel, Field
from ..Database import SessionLocal
from sqlalchemy.orm import session
from typing import Annotated
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags = ["admin"]
    )

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todo(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorize")
    todo_data = db.query(Todos).all()
    return todo_data

@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_admin(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorize")
    todo_data = db.query(Todos).filter(Todos.id == todo_id ).first()
    if todo_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    db.query(Todos).filter(Todos.id == todo_id ).delete()
    db.commit()