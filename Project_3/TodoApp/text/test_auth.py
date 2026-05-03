from datetime import timedelta, timezone, datetime
from .utils import *
from fastapi import HTTPException, status
from ..routers.auth import get_db, authonticate_user, create_access_token, SECRET_KEY, ALGORITHEM, get_current_user
from sqlalchemy.exc import IntegrityError
from jose import jwt
import pytest


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


def test_create_access_token():
    expires_delta=timedelta(minutes=15)
    acces_tokec = create_access_token(username="testuser", user_id=1, role="user", expires_delta=expires_delta)
    assert acces_tokec is not None
    decode_tokec = jwt.decode(acces_tokec, SECRET_KEY, algorithms=[ALGORITHEM], options={"verify_exp": False})
    assert decode_tokec["sub"] == "testuser"
    assert decode_tokec["id"] == 1
    assert decode_tokec["role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_tocken_varification():
    encode = {"sub": "username", "id": "1", "role": "Admin"}
    expires_delta  = timedelta(minutes=15)
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    token =  jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHEM)
    user = await get_current_user(token)
    assert user["username"] == "username" 
    assert user["id"] == "1"
    assert user["user_role"] == "Admin"


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_payload():
    encode = {"sub": "username"}
    token =  jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHEM)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate user"
