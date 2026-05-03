from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..Database import Base
from ..main import app
from ..models import Todos, Users
from ..routers.auth import bcrypt_context
import pytest
from fastapi.testclient import TestClient

# Database connection with sqlite -----------  start -----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./testtodoApp.db"
engine  = create_engine(SQLALCHEMY_DATABASE_URL, 
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
# Database connection with sqlite -----------  end -----------


TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(bind=engine)

def overwrite_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

def overried_get_current_user():
    return {"username": "deepaksinghpatel052", "id":"1", "user_role": "Admin"}


client = TestClient(app)



@pytest.fixture
def test_todo():
    db = TestSessionLocal()
    todo_item = Todos(title="Test Todo", description="This is a test todo item", priority=1, complete=False, owner_id=1)
    db.add(todo_item)
    db.commit()
    db.refresh(todo_item)
    yield todo_item
    with engine.connect() as connection:
         connection.execute(Todos.__table__.delete())
         connection.commit()

@pytest.fixture
def test_user():
    db = TestSessionLocal()
    user_item = Users(email="deepak@gmail.com", username="deepaksinghpatel052", 
                      first_name="Test", last_name="User", 
                      heshed_password = bcrypt_context.hash("testpassword"),
                      is_active=True, role="Admin")
    db.add(user_item)
    db.commit()
    yield user_item
    with engine.connect() as connection:
         connection.execute(Users.__table__.delete())
         connection.commit()        