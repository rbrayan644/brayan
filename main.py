from fastapi import FastAPI, HTTPException, Depends, Body, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from ctrl_db import (
    get_all_notes,
    get_note_by_id,
    create_note,
    update_note,
    delete_note
)


# Configuración del app
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Plantillas
templates = Jinja2Templates(directory="templates")

# Seguridad y autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos Pydantic
class NoteCreate(BaseModel):
    id_usuario: int
    titulo: str
    contenido: str

class Note(BaseModel):
    id: int
    id_usuario: int
    titulo: str
    contenido: str
    fecha_creacion: str
    fecha_actualizacion: str

class User(BaseModel):
    username: str
    password: str

# Crear JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia de seguridad
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Endpoints
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)  # Define authenticate_user
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Rutas protegidas
@app.get("/notes/", response_model=List[Note])
def get_notes(current_user: str = Depends(get_current_user)):
    notes = get_all_notes()
    if not notes:
        raise HTTPException(status_code=404, detail="No hay notas disponibles")
    return notes

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, current_user: str = Depends(get_current_user)):
    note = get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")