# use_cases/perfil.py

from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.get("/me")
def get_perfil_usuario(request: Request):
    user = request.state.user

    if user.get("is_professor") is True:
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")

    return {
        "mensagem": "Perfil do aluno autenticado",
        "usuario": {
            "username": user["username"],
            "email": user.get("email", "desconhecido"),
            "professor": user["is_professor"],
            "creditos": user.get("creditos", 0)
        }
    }
