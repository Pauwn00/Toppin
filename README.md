
# Toppin - API de Citas para Parejas

**Toppin** es una aplicación de citas diferente: diseñada para parejas que quieren conocer a otras parejas con intereses similares. Esta API permite registrar usuarios, gestionar intereses y descubrir matches compatibles.

---

## Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/)
- Python 3.10+
- JSON como almacenamiento persistente (simula base de datos)
- Uvicorn como servidor ASGI

---

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/paumt/toppin-api.git
   cd toppin-api
   ```

2. **Crea y activa un entorno virtual**:

   - En Windows:
     ```bash
     python -m venv env
     .\env\Scripts\activate
     ```

   - En macOS/Linux:
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Levanta el servidor**:
   ```bash
   uvicorn main:app --reload
   ```

5. Abre tu navegador en:  
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

##  Endpoints principales

| Método | Ruta         | Descripción                                |
|--------|--------------|--------------------------------------------|
| POST   | `/signup`    | Registro de pareja                         |
| POST   | `/login`     | Autenticación con email y password         |
| POST   | `/interests` | Añadir intereses (requiere token)          |
| POST    | `/like/{email}`   | Dar like a una pareja (requiere token)   |
| GET    | `/likes`   | Ver los likes dados (requiere token)   |
| GET    | `/matches`   | Ver parejas compatibles (requiere token)   |
| GET    | `/mutual-matches`   | Ver parejas que os habeis dado like entre vosotros (requiere token)   |



> Todos los endpoints protegidos usan token tipo Bearer (devolverá `/login`).

---

##  Persistencia

Los usuarios registrados y sus intereses se guardan en un archivo `usuarios.json`. Esto permite que los datos persistan entre reinicios del servidor sin necesidad de una base de datos real.

---

##  Ejemplo de uso

1. Registra una pareja:
   ```json
   {
     "email": "pareja@example.com",
     "password": "123456",
     "names": ["Ana", "Luis"],
     "interests": ["cine"]
   }
   ```

2. Inicia sesión en login, username sera nuestro correo y despues nos dirigiremos a Authorize y haremos lo mismo.

3. Usa ese token para añadir más intereses o ver matches compatibles.

4. Si queremos añadir un interes mas tarde lo redactariamos de esta manera:

      ```json
   {
     "tags":["motos","cine"]
   }
   ```

---

## Mejoras posibles

- Tests automáticos
- Dockerización del entorno

---

## Autor

Desarrollado por **Pau Martí**  
GitHub: [https://github.com/Pauwn00]

---

