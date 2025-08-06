# use_cases/protegida.py

from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/protegida")
def rota_protegida(request: Request):
    user = request.state.user
    return {
        "mensagem": f"Acesso permitido!",
        "usuario": {
            "username": user["username"],
            "id": user["sub"],
            "professor": user["is_professor"]
        }
    }
