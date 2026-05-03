from .utils import *
from fastapi import status
from ..routers.admin import get_db, get_current_user


app.dependency_overrides[get_db] = overwrite_get_db
app.dependency_overrides[get_current_user] = overried_get_current_user


def test_get_all_todo_by_admin(test_todo):
    response = client.get("/admin/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'description': 'This is a test todo item', 'title': 'Test Todo',
                                 'complete': False, 'priority': 1, 'id': 1, 'owner_id': 1}]
    
def test_delete_todo_by_admin(test_todo):
    response = client.delete("/admin/delete/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db  = TestSessionLocal()
    todo_item = db.query(Todos).filter(Todos.id == 1).first()
    assert todo_item is None

    response = client.delete("/admin/delete/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo item not found"}