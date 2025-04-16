
from pydantic import BaseModel
from typing import List

class ParejaRegistro(BaseModel):  # 👈 Para registrar
    email: str
    password: str
    names: List[str]
    interests: List[str] = []

class Pareja(BaseModel):  # 👈 Para devolver o manejar internamente
    email: str
    password: str
    names: List[str]
    interests: List[str] = []
    likes: List[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
