from typing import Optional

from pydantic import BaseModel


# Pydantic Model to use for request body
class UserBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Using to create a user
class UserCreate(UserBase):
    password: str


# Using to update a user
class UserUpdate(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None


# Full data about user, exclude password
class User(UserBase):
    id: int

    # Usses it, to display data e.g user.username instead of user['username']
    class Config:
        orm_mode = True
