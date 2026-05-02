from fastapi import FastAPI
import models
from Database import engine
from routers import auth, Todos, admin, users

app = FastAPI()

# Create database
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(Todos.router)
app.include_router(admin.router)
app.include_router(users.router)

