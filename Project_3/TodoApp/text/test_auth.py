from .utils import *
from fastapi import status
from ..routers.auth import get_db, authonticate_user
from sqlalchemy.exc import IntegrityError

app.dependency_overrides[get_db] = overwrite_get_db


def test_authonticate_user(test_user):
    db = TestSessionLocal()
    user = authonticate_user(test_user.username,"testpassword", db)
    assert user is not None
    assert user.username == "deepaksinghpatel052"

    # test with wrong password
    user = authonticate_user(test_user.username,"wrongpassword", db)
    assert user is False

    # test with wrong username
    user = authonticate_user("wrongusername","testpassword", db)
    assert user is False

def test_create_user(test_user):
    user_json = {
                "email": "example1@gmail.com",
                "username": "example1",
                "first_name": "Deepak",
                "last_name": "Patel",
                "password": "abc@123",
                "role": "user"
                }

    response = client.post("/auth/create_user", json=user_json)
    assert response.status_code == status.HTTP_201_CREATED
    db  = TestSessionLocal()
    created_user = db.query(Users).filter(Users.username == user_json["username"]).first()
    assert created_user is not None
    assert created_user.email == user_json["email"]
    assert created_user.first_name == user_json["first_name"]
    assert created_user.last_name == user_json["last_name"]
    assert created_user.role == user_json["role"]
    
    
    # Create user with same username should raise IntegrityError
    try:
        response = client.post("/auth/create_user", json=user_json)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    except IntegrityError:
        assert True
    
    db.delete(created_user)
    db.commit()


def test_create_access_token(test_user):
    data={"username": test_user.username, "password": "testpassword"}
    response = client.post("/auth/token", data=data)
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_create_access_token_with_wrong_credentials(test_user):
    data={"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/auth/token", data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate user"}