from fastapi import FastAPI
from models import Base
from database import engine
from routers import owners, pets

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(owners.router)
app.include_router(pets.router)

