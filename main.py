from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect

from use_cases.registro import router as registro_router
#from models.user import User

app = FastAPI()

# Conectar ao MongoDB
connect(db="LinguasII", host="mongodb+srv://liviagcarvalho:12345@cluster.sfj2axl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster")

# CORS (Não se preocupe com isso por enquanto, é uma configuração de segurança que permite que o frontend acesse a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API do Sistema de Línguas II esta funcionando!"}

app.include_router(registro_router)





# # Configurações do JWT
# SECRET_KEY = "sua_chave_secreta_muito_segura_aqui_mude_em_producao"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# security = HTTPBearer()

# # Schemas Pydantic
# class UserRegister(BaseModel):
#     full_name: str
#     username: str
#     email: EmailStr
#     password: str
#     confirm_password: str
#     user_type: str  # 'aluno' ou 'professor'
    
#     @validator('user_type')
#     def validate_user_type(cls, v):
#         if v not in ['aluno', 'professor']:
#             raise ValueError('user_type deve ser "aluno" ou "professor"')
#         return v
    
#     @validator('confirm_password')
#     def passwords_match(cls, v, values):
#         if 'password' in values and v != values['password']:
#             raise ValueError('Senhas não coincidem')
#         return v
    
#     @validator('password')
#     def validate_password(cls, v):
#         if len(v) < 6:
#             raise ValueError('Senha deve ter pelo menos 6 caracteres')
#         return v

# class UserLogin(BaseModel):
#     username: str
#     password: str

# class UserResponse(BaseModel):
#     id: str
#     full_name: str
#     username: str
#     email: str
#     user_type: str
#     credits: Optional[int] = None
#     created_at: str
#     is_active: bool

# class LoginResponse(BaseModel):
#     message: str
#     user: UserResponse
#     access_token: str
#     token_type: str = "bearer"

# class MessageResponse(BaseModel):
#     message: str

# # Funções de autenticação
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     """Cria um token JWT"""
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def verify_token(token: str) -> dict:
#     """Verifica e decodifica um token JWT"""
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token inválido",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return payload
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token inválido",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Obtém o usuário atual baseado no token"""
#     token = credentials.credentials
#     payload = verify_token(token)
#     username = payload.get("sub")
    
#     user = User.objects(username=username, is_active=True).first()
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Usuário não encontrado",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     return user

# def get_current_student(current_user: User = Depends(get_current_user)):
#     """Verifica se o usuário atual é um aluno"""
#     if current_user.user_type != 'aluno':
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Acesso negado. Apenas alunos podem acessar este recurso."
#         )
#     return current_user

# def get_current_teacher(current_user: User = Depends(get_current_user)):
#     """Verifica se o usuário atual é um professor"""
#     if current_user.user_type != 'professor':
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Acesso negado. Apenas professores podem acessar este recurso."
#         )
#     return current_user
