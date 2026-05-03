from fastapi import FastAPI
from .models import Base
from .Database import engine
from .routers import auth, Todos, admin, users

app = FastAPI()

# Create database
Base.metadata.create_all(bind=engine)


@app.get("/healthy")
async def helth_check():
    return {"status":"Healthy"}


app.include_router(auth.router)
app.include_router(Todos.router)
app.include_router(admin.router)
app.include_router(users.router)

