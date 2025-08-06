# middlewares/jwt_auth.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError

SECRET_KEY = "sua-chave-secreta-aqui"
ALGORITHM = "HS256"

# Rotas públicas que não exigem token
ROTAS_PUBLICAS = ["/login", "/register", "/docs", "/openapi.json"]

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ROTAS_PUBLICAS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Token não fornecido."})

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload  # coloca o payload para ser usado nas rotas
        except JWTError:
            return JSONResponse(status_code=403, content={"detail": "Token inválido ou expirado."})

        return await call_next(request)
