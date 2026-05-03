from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos
from pydantic import BaseModel, Field
from ..Database import SessionLocal
from sqlalchemy.orm import session
from typing import Annotated
from starlette import status
from .auth import get_current_user

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(current_uiser: user_dependency, db: db_dependency):
    if current_uiser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
    return db.query(Todos).filter(Todos.owner_id==current_uiser.get("id")).all()


@router.get("/get_todo_by_id/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(current_uiser: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if current_uiser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authonticate")
    todo_model =  db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id==current_uiser.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo tiem not found")



class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=6)
    complete: bool



@router.post("/todo/create_new", status_code=status.HTTP_201_CREATED)
async def create_new_todo(current_uiser: user_dependency, db: db_dependency, TodoRequest: TodoRequest):
    if current_uiser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authonticate")
    todo_data = Todos(**TodoRequest.model_dump(), owner_id=current_uiser.get("id"))
    db.add(todo_data)
    db.commit()


@router.put("/todo/update_todu/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()


@router.delete("/todo/delete_todu/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()


