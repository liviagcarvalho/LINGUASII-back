# middlewares/jwt_auth.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError

SECRET_KEY = "sua-chave-secreta-aqui"
ALGORITHM = "HS256"

# Rotas públicas (sem autenticação)
PUBLIC_PATHS_EXACT = {
    "/login",
    "/register",
    "/openapi.json",
    "/aulas-publicas-sem-login",
}

# Prefixos públicos (qualquer subrota)
PUBLIC_PREFIXES = (
    "/docs",            # /docs, /docs/* (Swagger assets)
    "/redoc",           # se usar redoc
)

def is_public_path(path: str) -> bool:
    # normaliza e aceita com ou sem barra final
    p = path.rstrip("/") or "/"
    if p in PUBLIC_PATHS_EXACT:
        return True
    return any(p.startswith(prefix) for prefix in PUBLIC_PREFIXES)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Se a rota é pública, libera SEM olhar Authorization
        if is_public_path(path):
            return await call_next(request)

        # Demais rotas exigem Bearer token válido
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Token não fornecido."})

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload
        except JWTError:
            return JSONResponse(status_code=403, content={"detail": "Token inválido ou expirado."})

        return await call_next(request)
