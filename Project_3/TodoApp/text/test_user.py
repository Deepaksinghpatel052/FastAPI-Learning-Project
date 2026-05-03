from .utils import *
from fastapi import status
from ..routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = overwrite_get_db
app.dependency_overrides[get_current_user] = overried_get_current_user

 
def test_get_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id":test_user.id, "email":test_user.email, 
                                "username":test_user.username, "first_name":test_user.first_name, 
                                "last_name":test_user.last_name, "is_active":test_user.is_active,
                                "role":test_user.role}


def test_user_changed_password(test_user):
    response = client.put("/user/change_password", json={"current_password": "testpassword", 
                                                         "new_password": "newtestpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    user_info = db.query(Users).filter(Users.id==test_user.id).first()
    assert bcrypt_context.verify("newtestpassword", user_info.heshed_password) == True

def test_user_changed_password_with_wrong_current_password(test_user):
    response = client.put("/user/change_password", json={"current_password": "wrongpassword", "new_password": "newtestpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password changed"}