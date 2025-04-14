
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import uuid
import json
import os
from passlib.context import CryptContext

app = FastAPI()

# -------------------------
# Seguridad con bcrypt
# -------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Estructura de datos
# -------------------------

class Pareja(BaseModel):
    email: str
    password: str
    names: List[str]
    interests: List[str] = []
    likes: List[str] = []

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
        try:
            with open(FILE_PATH, "r") as f:
                data = json.load(f)
                for email, info in data.items():
                    usuarios[email] = Pareja(**info)
        except json.JSONDecodeError:
            print("⚠️ Archivo JSON vacío o corrupto. Se ignora.")

# Cargamos al iniciar
cargar_usuarios()

# -------------------------
# Endpoints
# -------------------------

@app.post("/signup")
def registrar(pareja: Pareja):
    if pareja.email in usuarios:
        raise HTTPException(status_code=400, detail="Ya existe")
    
    hashed_password = pwd_context.hash(pareja.password)
    pareja.password = hashed_password

    usuarios[pareja.email] = pareja
    guardar_usuarios()
    return {"mensaje": "Registro exitoso"}

@app.post("/login", response_model=TokenResponse)
def loguearse(datos: OAuth2PasswordRequestForm = Depends()):
    p = usuarios.get(datos.username)
    if not p:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not pwd_context.verify(datos.password, p.password):
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
    
    nuevos = set(body["tags"])
    existentes = set(pareja_actual.interests)
    pareja_actual.interests = list(nuevos | existentes)
    
    guardar_usuarios()
    return {"msg": "Intereses actualizados", "intereses": pareja_actual.interests}

@app.post("/like/{email}")
def dar_like(email: str, pareja_actual = Depends(get_user)):
    if email not in usuarios:
        raise HTTPException(status_code=404, detail="Pareja no encontrada")
    if email == pareja_actual.email:
        raise HTTPException(status_code=400, detail="No puedes likearte a ti mismo")
    if email in pareja_actual.likes:
        return {"msg": "Ya le diste like antes"}
    
    pareja_actual.likes.append(email)
    guardar_usuarios()
    return {"msg": f"Le diste like a {email}"}

@app.get("/likes")
def ver_likes(pareja_actual = Depends(get_user)):
    return {"likes": pareja_actual.likes}

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

@app.get("/mutual-matches")
def ver_matches_mutuos(pareja_actual = Depends(get_user)):
    lista = []
    for mail, otro in usuarios.items():
        if mail == pareja_actual.email:
            continue
        comunes = list(set(pareja_actual.interests) & set(otro.interests))
        if comunes and pareja_actual.email in otro.likes and otro.email in pareja_actual.likes:
            lista.append({
                "email": otro.email,
                "names": otro.names,
                "intereses_comunes": comunes
            })
    return lista
