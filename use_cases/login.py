# use_cases/login.py

from fastapi import APIRouter, HTTPException
from models.user import User
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Chave secreta para JWT
SECRET_KEY = "sua-chave-secreta-aqui"
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 60

# Modelo de entrada
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

# Modelo de saída (opcional)
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse)
async def login(dados: LoginRequest):
    user = User.objects(email=dados.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Email não encontrado.")

    if not bcrypt.checkpw(dados.senha.encode('utf-8'), user.senha.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Senha incorreta.")

    # Gerar token JWT

    payload = {
    "sub": str(user.id),
    "username": user.username,
    "email": user.email,
    "is_professor": user.is_professor,
    "creditos": user.creditos,
    "exp": datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
    }   


    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}
