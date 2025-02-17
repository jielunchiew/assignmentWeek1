from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)


class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("owners.id"))
    breed = Column(String)
    date_created = Column(DateTime)
    date_modified = Column(DateTime)

