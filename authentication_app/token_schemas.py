from typing import Optional

from pydantic import BaseModel


# Creates a Token Response body
class Token(BaseModel):
    access_token: str
    token_type: str

# Creates a Token
class TokenData(BaseModel):
    username: Optional[str] = None