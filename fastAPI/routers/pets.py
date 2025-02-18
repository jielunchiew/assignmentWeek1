from datetime import datetime
from typing import Annotated, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from models import Pets, Owners
from starlette import status


router = APIRouter(
    prefix = '/pet',
    tags = ['pet']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class PetRequest(BaseModel):
    name: str = Field(..., min_length=1) 
    owner_id: int = Field(..., gt=0)  
    breed: str = Field(..., min_length=1)  

# Read all pets for a certain owner
@router.get("/get-pets/{owner_id}", status_code=status.HTTP_200_OK) #Find by owner id
async def get_pets(owner_id: Annotated[int, Path(..., gt=0)], db: db_dependency):
    owner = db.query(Owners).filter(Owners.id == owner_id).first()

    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    
    pets = db.query(Pets).filter(Pets.owner_id == owner_id).all()

    if pets is not None:
        return pets
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pets found for this owner")


# User can find all pets belonging to a certain owner
@router.get("/all-pets/{owner_name}",status_code=status.HTTP_200_OK) #Find by owner name
async def get_all_pets(owner_name: Annotated[str, Path(min_length=1)], db: db_dependency):
    owner = db.query(Owners).filter(
        func.lower(func.concat(Owners.first_name, ' ', Owners.last_name)) == func.lower(owner_name)
    ).first()

    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
    
    pets = db.query(Pets).filter(Pets.owner_id == owner.id).all()

    if pets is not None:
        return pets
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pets found for this owner")

# User can find owner of a certain pet (by name or id)
@router.get("/pet-owner/", status_code=status.HTTP_200_OK)
async def get_owner_of_pet(db: db_dependency, pet_id: Union[int, None] = Query(default=None), pet_name: Union[str, None] = Query(default=None)):
    if pet_id is not None:
        pet = db.query(Pets).filter(Pets.id == pet_id).first()
    elif pet_name is not None:
        pet = db.query(Pets).filter(Pets.name == pet_name).first()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide either pet_id or pet_name")
   
    if pet :
        return pet

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pet found")


# User can update existing pets that belongs to a certain owner
@router.put("/update-pet/{pet_id}", status_code=status.HTTP_200_OK)
async def update_pet(pet_id: Annotated[int, Path(..., gt=0)], pet: PetRequest, db: db_dependency):
    try:
        owner = db.query(Owners).filter(Owners.id == pet.owner_id).first()

        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")

        current_time = datetime.now()

        updated = db.query(Pets).filter(Pets.id == pet_id).update({
            "name": pet.name,
            "owner_id": pet.owner_id,
            "breed": pet.breed,
            "date_modified": current_time
        })

        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

        db.commit()
        return {"message": "Pet updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# User can delete existing pets from existing owner
@router.delete("/delete-pet/{pet_id}", status_code=status.HTTP_200_OK)
async def delete_pet(pet_id: Annotated[int, Path(gt=0)], db: db_dependency):
    try:
        deleted = db.query(Pets).filter(Pets.id == pet_id).delete()

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

        db.commit()
        return {"message": "Pet deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# User can create new pets for existing owner using API
@router.post('/create-pet', status_code=status.HTTP_201_CREATED)
async def create_pet(pet: PetRequest, db: db_dependency):
    try:
        owner = db.query(Owners).filter(Owners.id == pet.owner_id).first()

        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
        
        current_time = datetime.now()

        new_pet = Pets(
            name = pet.name,
            owner_id = pet.owner_id,
            breed = pet.breed,
            date_created = current_time,
            date_modified = current_time
        )

        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)
        return {
            "message": "Pet created successfully",
            "pet": new_pet
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))