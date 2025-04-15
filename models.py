
from pydantic import BaseModel
from typing import List

class Pareja(BaseModel):
    email: str
    password: str
    names: List[str]
    interests: List[str] = []
    likes: List[str] = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

usuarios = {}  # Diccionario global que simula la base de datos
