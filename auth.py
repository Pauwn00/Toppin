
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import uuid
from models import TokenResponse, usuarios, Pareja
from utils import guardar_usuarios

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = OAuth2PasswordBearer(tokenUrl="login")
tokens = {}

def get_user(token: str = Depends(auth_scheme)):
    user_email = tokens.get(token)
    if not user_email:
        raise HTTPException(status_code=403, detail="Token no válido")
    return usuarios[user_email]

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def login(datos: OAuth2PasswordRequestForm):
    p = usuarios.get(datos.username)
    if not p or not verify_password(datos.password, p.password):
        raise HTTPException(status_code=403, detail="Credenciales incorrectas")
    
    tkn = str(uuid.uuid4())
    tokens[tkn] = datos.username
    return {"access_token": tkn, "token_type": "bearer"}
