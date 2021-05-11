# Create model attributes/column
from sqlalchemy import Column, Integer, String

from .database import Base


# User Model
class User(Base):
    __tablename__ = "users"  # tells SQLAlchemy the name of the table to use in the database

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    hashed_password = Column(String)
