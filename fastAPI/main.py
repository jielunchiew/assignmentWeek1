from fastapi import FastAPI
import models
from database import engine, SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/create_owner/")
async def create_owner(owner: models.Owner):
    db = SessionLocal()
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner