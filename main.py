from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import uuid
import json
import os

app = FastAPI()

# -------------------------
# Estructura de datos
# -------------------------

class Pareja(BaseModel):
    email: str
    password: str
    names: List[str]
    interests: List[str] = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# -------------------------
# Base de datos simulada
# -------------------------

usuarios = {}  # email -> Pareja
tokens = {}  # token -> email
auth_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -------------------------
# Archivos de persistencia
# -------------------------

FILE_PATH = "usuarios.json"

def guardar_usuarios():
    with open(FILE_PATH, "w") as f:
        json.dump({k: v.dict() for k, v in usuarios.items()}, f)

def cargar_usuarios():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            data = json.load(f)
            for email, info in data.items():
                usuarios[email] = Pareja(**info)

# Cargamos al iniciar
cargar_usuarios()

# -------------------------
# Endpoints
# -------------------------

@app.post("/signup")
def registrar(pareja: Pareja):
    if pareja.email in usuarios:
        raise HTTPException(status_code=400, detail="Ya existe")
    usuarios[pareja.email] = pareja
    guardar_usuarios()
    return {"mensaje": "ok"}

@app.post("/login", response_model=TokenResponse)
def loguearse(datos: OAuth2PasswordRequestForm = Depends()):
    p = usuarios.get(datos.username)
    if not p:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if p.password != datos.password:
        raise HTTPException(status_code=403, detail="Contraseña incorrecta")
    
    tkn = str(uuid.uuid4())
    tokens[tkn] = datos.username
    return {"access_token": tkn, "token_type": "bearer"}

def get_user(token: str = Depends(auth_scheme)):
    user_email = tokens.get(token)
    if not user_email:
        raise HTTPException(status_code=403, detail="Token no válido")
    return usuarios[user_email]

@app.post("/interests")
def guardar_intereses(body: dict, pareja_actual = Depends(get_user)):
    if "tags" not in body:
        raise HTTPException(status_code=400, detail="Faltan tags")
    
    # Fusionar intereses sin duplicados
    nuevos = set(body["tags"])
    existentes = set(pareja_actual.interests)
    pareja_actual.interests = list(nuevos | existentes)
    
    guardar_usuarios()
    return {"msg": "Intereses actualizados", "intereses": pareja_actual.interests}

@app.get("/matches")
def ver_matches(pareja_actual = Depends(get_user)):
    lista = []
    for mail, otro in usuarios.items():
        if mail == pareja_actual.email:
            continue
        comunes = list(set(pareja_actual.interests) & set(otro.interests))
        if comunes:
            lista.append({
                "email": otro.email,
                "names": otro.names,
                "intereses_comunes": comunes
            })
    return lista
