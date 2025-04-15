
import json
import os
from models import usuarios, Pareja

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
