# use_cases/registro.py

from fastapi import APIRouter, HTTPException
from models.user import User
from pydantic import BaseModel, EmailStr
import bcrypt

router = APIRouter()

# Modelo de entrada com Pydantic
class RegistroRequest(BaseModel):
    email: EmailStr
    username: str
    nome: str
    senha: str

@router.post("/register")
async def registrar_usuario(dados: RegistroRequest):
    # Verificar se o email já existe
    if User.objects(email=dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    if User.objects(username=dados.username).first():
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")

    # Hash da senha
    senha_hash = bcrypt.hashpw(dados.senha.encode('utf-8'), bcrypt.gensalt())

    # Criar usuário (is_professor fixo como False)
    novo_usuario = User(
    email=dados.email,
    username=dados.username,
    nome=dados.nome,
    senha=senha_hash.decode('utf-8'),
    is_professor=False,
    creditos=0  # novo campo
    )

    novo_usuario.save()

    return {"mensagem": "Usuário cadastrado com sucesso."}
