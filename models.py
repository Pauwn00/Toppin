
from sqlalchemy import Column, String
from sqlalchemy.types import JSON
from database import Base

class ParejaORM(Base):
    __tablename__ = "parejas"

    email = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    names = Column(JSON, default=[])
    interests = Column(JSON, default=[])
    likes = Column(JSON, default=[])
