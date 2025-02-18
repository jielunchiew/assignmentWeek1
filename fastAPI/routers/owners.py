from typing import Annotated
from pydantic import BaseModel, Field, condate
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Owners
from starlette import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime, date


router = APIRouter(
    prefix = '/owner',
    tags = ['owner']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class OwnerRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)

# Read all owners
@router.get("/owners", status_code = status.HTTP_200_OK)
async def get_owners(db: db_dependency):
     users = db.query(Owners).all()

     if users is not None:
         return users
     
     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No owners found")

# User can create new owner using API
@router.post('/create-owner', status_code = status.HTTP_201_CREATED)
async def create_owner(owner: OwnerRequest, db: db_dependency):
    try:
        current_time =datetime.now()

        new_owner = Owners(
            first_name = owner.first_name,
            last_name = owner.last_name,
            date_created = current_time,
            date_modified = current_time
        )

        db.add(new_owner)
        db.commit()
        db.refresh(new_owner)

        return {
            "message": "Owner created successfully",
            "owner": new_owner
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Find owners the user created on a particular date
@router.get("/find-owner/{date_created}", status_code=status.HTTP_200_OK)
async def find_owner(date_created: Annotated[date, Path()], db: db_dependency):
    owner = db.query(Owners).filter(
        func.date(Owners.date_created) == date_created
    ).all()

    if owner is not None:
        return owner
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
