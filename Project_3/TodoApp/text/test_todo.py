from ..routers.Todos import get_db, get_current_user
from ..main import app
from fastapi import status
from ..models import Todos
from .utils import *



app.dependency_overrides[get_db] = overwrite_get_db
app.dependency_overrides[get_current_user] = overried_get_current_user



def test_read_all_todo(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'description': 'This is a test todo item', 'title': 'Test Todo',
                                 'complete': False, 'priority': 1, 'id': 1, 'owner_id': 1}]



def test_get_todo_by_id(test_todo):
    response = client.get("/get_todo_by_id/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'description': 'This is a test todo item', 'title': 'Test Todo',
                                 'complete': False, 'priority': 1, 'id': 1, 'owner_id': 1}

def test_get_todo_by_wrong_id(test_todo):
    response = client.get("/get_todo_by_id/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_todo_by_string_id(test_todo):
    response = client.get("/get_todo_by_id/sdcd")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_get_todo_by_negitave_id(test_todo):
    response = client.get("/get_todo_by_id/-3")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_create_new_todo(test_todo):
    requset_body = {"title": "New Todo", "description": "This is a new todo item", "priority": 2, "complete": False}
    response = client.post("/todo/create_new", json=requset_body)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == None

    db  = TestSessionLocal()
    todo_item = db.query(Todos).filter(Todos.id == 2).first()
    assert todo_item is not None
    assert todo_item.title == requset_body["title"]
    assert todo_item.description == requset_body["description"]
    assert todo_item.priority == requset_body["priority"]
    assert todo_item.complete == requset_body["complete"]
    db.query(Todos).filter(Todos.id == 2).delete()
    db.commit()
    db.close()  


def test_update_todo(test_todo):
    update_request_body = {"title": "Change the title of todo already saved", 
                           "description": "This is a test todo item", 
                           "priority": 5, 
                           "complete": False}
    response = client.put("/todo/update_todu/1", json=update_request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db  = TestSessionLocal()
    updated_todo_item = db.query(Todos).filter(Todos.id == 1).first()
    assert updated_todo_item is not None
    assert updated_todo_item.title == update_request_body["title"]
    assert updated_todo_item.description == update_request_body["description"]
    assert updated_todo_item.priority == update_request_body["priority"]
    assert updated_todo_item.complete == update_request_body["complete"]

    response = client.put("/todo/update_todu/-1", json=update_request_body)
    assert response.json() == {'detail': [{'type': 'greater_than', 'loc': ['path', 'todo_id'], 'msg': 'Input should be greater than 0', 'input': '-1', 'ctx': {'gt': 0}}]}

    response = client.put("/todo/update_todu/899", json=update_request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo item not found'}


def test_delete_todo(test_todo):
    response = client.delete("/todo/delete_todu/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT                   
    db  = TestSessionLocal()
    deleted_todo_item = db.query(Todos).filter(Todos.id == 1).first()
    assert deleted_todo_item is None

    response = client.delete("/todo/delete_todu/-1")
    assert response.json() == {'detail': [{'type': 'greater_than', 'loc': ['path', 'todo_id'], 'msg': 'Input should be greater than 0', 'input': '-1', 'ctx': {'gt': 0}}]}

    response = client.delete("/todo/delete_todu/899")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo item not found'} 