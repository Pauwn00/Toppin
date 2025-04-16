from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Column, String
from sqlalchemy.types import JSON
from database import Base

class ParejaORM(Base):
    __tablename__ = "parejas"

    email = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    names = Column(MutableList.as_mutable(JSON), default=[])       
    interests = Column(MutableList.as_mutable(JSON), default=[])   
    likes = Column(MutableList.as_mutable(JSON), default=[])     
