# use_cases/protegida.py

from fastapi import APIRouter, Request
from middlewares.jwt_auth import JWTMiddleware
from fastapi import Depends

router = APIRouter()

@router.get("/protegida")
def rota_protegida(request: Request, dependencies=[Depends(JWTMiddleware)]):
    user = request.state.user
    return {
        "mensagem": f"Acesso permitido!",
        "usuario": {
            "username": user["username"],
            "id": user["sub"],
            "professor": user["is_professor"]
        }
    }
