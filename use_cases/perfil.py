# use_cases/perfil.py

from fastapi import APIRouter, Request, HTTPException, Body
from models.user import User

router = APIRouter()

@router.get("/me")
def get_perfil_usuario(request: Request):
    user = request.state.user

    if user.get("is_professor") is True:
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")

    # Buscar o usuário real do banco para garantir os créditos atualizados
    usuario_db = User.objects(id=user["sub"]).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {
        "mensagem": "Perfil do aluno autenticado",
        "usuario": {
            "username": usuario_db.username,
            "email": usuario_db.email,
            "professor": usuario_db.is_professor,
            "creditos": usuario_db.creditos
        }
    }

@router.post("/comprar-creditos")
def adicionar_creditos(request: Request, quantidade: int = Body(...)):
    user = request.state.user

    if user.get("is_professor") is True:
        raise HTTPException(status_code=403, detail="Apenas alunos podem comprar créditos.")

    usuario_db = User.objects(id=user["sub"]).first()

    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario_db.creditos += quantidade
    usuario_db.save()

    return {
        "mensagem": "Créditos adicionados com sucesso.",
        "creditos": usuario_db.creditos
    }
