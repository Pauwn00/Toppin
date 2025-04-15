
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid

from database import SessionLocal, engine
from models import Base, ParejaORM
from schemas import Pareja, TokenResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
tokens = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = tokens.get(token)
    if not email:
        raise HTTPException(status_code=403, detail="Token no válido")
    user = db.query(ParejaORM).filter(ParejaORM.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.post("/signup")
def registrar(pareja: Pareja, db: Session = Depends(get_db)):
    if db.query(ParejaORM).filter(ParejaORM.email == pareja.email).first():
        raise HTTPException(status_code=400, detail="Ya existe")
    
    hashed_password = pwd_context.hash(pareja.password)
    db_pareja = ParejaORM(
        email=pareja.email,
        password=hashed_password,
        names=pareja.names,
        interests=pareja.interests,
        likes=[]
    )
    db.add(db_pareja)
    db.commit()
    return {"mensaje": "Registro exitoso"}

@app.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(ParejaORM).filter(ParejaORM.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Credenciales inválidas")
    
    token = str(uuid.uuid4())
    tokens[token] = user.email
    return {"access_token": token, "token_type": "bearer"}

@app.post("/interests")
def guardar_intereses(body: dict, pareja = Depends(get_user_from_token), db: Session = Depends(get_db)):
    if "tags" not in body:
        raise HTTPException(status_code=400, detail="Faltan tags")
    
    nuevos = set(body["tags"])
    existentes = set(pareja.interests)
    pareja.interests = list(nuevos | existentes)
    db.commit()
    return {"msg": "Intereses actualizados", "intereses": pareja.interests}

@app.post("/like/{email}")
def dar_like(email: str, pareja = Depends(get_user_from_token), db: Session = Depends(get_db)):
    if email == pareja.email:
        raise HTTPException(status_code=400, detail="No puedes likearte a ti mismo")
    objetivo = db.query(ParejaORM).filter(ParejaORM.email == email).first()
    if not objetivo:
        raise HTTPException(status_code=404, detail="Pareja no encontrada")
    if email in pareja.likes:
        return {"msg": "Ya le diste like antes"}
    pareja.likes.append(email)
    db.commit()
    return {"msg": f"Le diste like a {email}"}

@app.get("/likes")
def ver_likes(pareja = Depends(get_user_from_token)):
    return {"likes": pareja.likes}

@app.get("/matches")
def ver_matches(pareja = Depends(get_user_from_token), db: Session = Depends(get_db)):
    lista = []
    parejas = db.query(ParejaORM).all()
    for otra in parejas:
        if otra.email == pareja.email:
            continue
        comunes = list(set(pareja.interests) & set(otra.interests))
        if comunes:
            lista.append({
                "email": otra.email,
                "names": otra.names,
                "intereses_comunes": comunes
            })
    return lista

@app.get("/mutual-matches")
def ver_matches_mutuos(pareja = Depends(get_user_from_token), db: Session = Depends(get_db)):
    lista = []
    parejas = db.query(ParejaORM).all()
    for otra in parejas:
        if otra.email == pareja.email:
            continue
        comunes = list(set(pareja.interests) & set(otra.interests))
        if comunes and pareja.email in otra.likes and otra.email in pareja.likes:
            lista.append({
                "email": otra.email,
                "names": otra.names,
                "intereses_comunes": comunes
            })
    return lista
