
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import Pareja, usuarios
from auth import login, get_user, hash_password
from utils import guardar_usuarios, cargar_usuarios

app = FastAPI()

# Cargar datos al iniciar
cargar_usuarios()

@app.post("/signup")
def registrar(pareja: Pareja):
    if pareja.email in usuarios:
        raise HTTPException(status_code=400, detail="Ya existe")

    pareja.password = hash_password(pareja.password)
    usuarios[pareja.email] = pareja
    guardar_usuarios()
    return {"mensaje": "Registro exitoso"}

@app.post("/login")
def login_route(datos: OAuth2PasswordRequestForm = Depends()):
    return login(datos)

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
