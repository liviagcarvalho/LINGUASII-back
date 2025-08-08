# # use_cases/aula.py
# from fastapi import APIRouter, HTTPException, Request, Query
# from models.aula import Aula
# from models.user import User
# from pydantic import BaseModel, Field
# from datetime import datetime, timedelta
# from bson import ObjectId
# from typing import Optional

# router = APIRouter()

# class AulaCreateRequest(BaseModel):
#     tipo: str = Field(..., regex="^(particular|grupo)$")
#     lingua: str = Field(..., regex="^(ingles|espanhol)$")
#     data: datetime
#     professor_id: str
#     alunos_ids: list[str] = []  # default vazio
#     link_meet: Optional[str] = None  # <<< novo campo

# @router.post("/aulas")
# def criar_aula(payload: AulaCreateRequest, request: Request):
#     user = request.state.user
#     if not user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Apenas professores podem criar aulas.")

#     # Professor
#     try:
#         professor = User.objects.get(id=ObjectId(payload.professor_id))
#     except Exception:
#         raise HTTPException(status_code=404, detail="Professor não encontrado.")

#     if str(professor.id) != user["sub"]:
#         raise HTTPException(status_code=403, detail="Você só pode criar aulas como você mesmo.")

#     # Alunos (opcional)
#     alunos = []
#     for aluno_id in payload.alunos_ids:
#         try:
#             aluno = User.objects.get(id=ObjectId(aluno_id))
#             if aluno.is_professor:
#                 raise HTTPException(status_code=400, detail="Um professor não pode ser aluno.")
#             alunos.append(aluno)
#         except Exception:
#             raise HTTPException(status_code=404, detail=f"Aluno com ID {aluno_id} não encontrado.")

#     # Criar e salvar a aula
#     try:
#         aula = Aula(
#             tipo=payload.tipo,
#             lingua=payload.lingua,
#             data=payload.data,
#             professor=professor,
#             alunos=alunos,
#             link_meet=payload.link_meet,  # <<< salva o link (pode ser None)
#         )
#         aula.clean()   # define créditos e valida limites conforme tipo
#         aula.save()
#         return {"mensagem": "Aula criada com sucesso", "id": str(aula.id)}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Erro ao criar aula: {str(e)}")

# @router.delete("/aulas/{aula_id}")
# def deletar_aula(aula_id: str, request: Request):
#     user = request.state.user
#     if not user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Apenas professores podem deletar aulas.")

#     try:
#         aula = Aula.objects.get(id=ObjectId(aula_id))
#     except Exception:
#         raise HTTPException(status_code=404, detail="Aula não encontrada.")

#     if str(aula.professor.id) != user["sub"]:
#         raise HTTPException(status_code=403, detail="Você só pode deletar aulas criadas por você.")

#     try:
#         aula.delete()
#         return {"mensagem": "Aula deletada com sucesso"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao deletar aula: {str(e)}")

# @router.get("/minhas-aulas")
# def listar_aulas_professor(request: Request):
#     user = request.state.user
#     if not user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Apenas professores podem acessar suas aulas.")

#     try:
#         aulas = Aula.objects(professor=ObjectId(user["sub"])).order_by("+data")
#         return [
#             {
#                 "id": str(aula.id),
#                 "titulo": getattr(aula, "titulo", "Aula"),
#                 "data": aula.data.isoformat(),
#                 "tipo": aula.tipo,
#                 "lingua": aula.lingua,
#                 "creditos": aula.creditos,
#                 "link_meet": getattr(aula, "link_meet", None),  # <<< incluído
#             }
#             for aula in aulas
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao buscar aulas: {str(e)}")

# @router.get("/aulas-publicas")
# def listar_aulas_publicas(request: Request):
#     user = request.state.user
#     if user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Professores não podem reservar aulas.")

#     try:
#         agora = datetime.utcnow()
#         aulas = Aula.objects(data__gte=agora).order_by("+data")
#         return [
#             {
#                 "id": str(aula.id),
#                 "tipo": aula.tipo,
#                 "lingua": aula.lingua,
#                 "data": aula.data.isoformat(),
#                 "professor": str(aula.professor.id),
#                 "creditos": aula.creditos,
#                 "titulo": getattr(aula, "titulo", None),
#                 "link_meet": getattr(aula, "link_meet", None),  # <<< incluído
#             }
#             for aula in aulas
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao buscar aulas: {str(e)}")

# @router.post("/reservar/{aula_id}")
# def reservar_aula(aula_id: str, request: Request):
#     user = request.state.user
#     if user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Professores não podem reservar aulas.")

#     try:
#         aula = Aula.objects.get(id=ObjectId(aula_id))
#     except Exception:
#         raise HTTPException(status_code=404, detail="Aula não encontrada.")

#     try:
#         aluno = User.objects.get(id=ObjectId(user["sub"]))
#     except Exception:
#         raise HTTPException(status_code=404, detail="Aluno não encontrado.")

#     if aluno in aula.alunos:
#         raise HTTPException(status_code=400, detail="Você já está inscrito nesta aula.")

#     if aula.tipo == "particular" and len(aula.alunos) >= 1:
#         raise HTTPException(status_code=400, detail="Aula particular já está preenchida.")
#     if aula.tipo == "grupo" and len(aula.alunos) >= 4:
#         raise HTTPException(status_code=400, detail="Aula em grupo está cheia.")

#     if aluno.creditos < aula.creditos:
#         raise HTTPException(status_code=400, detail="Créditos insuficientes para reservar esta aula.")
    
#     try:
#         aluno.creditos -= aula.creditos
#         aluno.save()
#         aula.alunos.append(aluno)
#         aula.save()
#         return {
#             "mensagem": "Reserva realizada com sucesso",
#             "creditos_atualizados": aluno.creditos,
#             "aula": {
#                 "id": str(aula.id),
#                 "titulo": getattr(aula, "titulo", None),
#                 "tipo": aula.tipo,
#                 "lingua": aula.lingua,
#                 "data": aula.data.isoformat(),
#                 "creditos": aula.creditos,
#                 "link_meet": getattr(aula, "link_meet", None),  # <<< incluído
#             },
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao reservar aula: {str(e)}")

# @router.get("/aulas-publicas-sem-login")
# def listar_aulas_publicas_sem_login(
#     tipo: Optional[str] = Query(None, pattern="^(particular|grupo)$"),
#     lingua: Optional[str] = Query(None, pattern="^(ingles|espanhol)$"),
#     busca: Optional[str] = Query(None, description="Busca por título (case-insensitive)"),
#     data_de: Optional[str] = Query(None, description="YYYY-MM-DDTHH:MM:SS"),
#     data_ate: Optional[str] = Query(None, description="YYYY-MM-DDTHH:MM:SS"),
#     limit: int = Query(50, ge=1, le=200),
#     skip: int = Query(0, ge=0),
#     ordem: str = Query("asc", pattern="^(asc|desc)$"),
# ):
#     try:
#         qs = Aula.objects  # QuerySet base

#         # Filtros de data
#         if data_de:
#             try:
#                 dt = datetime.fromisoformat(data_de)
#                 qs = qs.filter(data__gte=dt)
#             except Exception:
#                 raise HTTPException(status_code=400, detail="Parâmetro 'data_de' inválido (use ISO 8601).")
#         if data_ate:
#             try:
#                 dt = datetime.fromisoformat(data_ate)
#                 qs = qs.filter(data__lte=dt)
#             except Exception:
#                 raise HTTPException(status_code=400, detail="Parâmetro 'data_ate' inválido (use ISO 8601).")

#         # Demais filtros
#         if tipo:
#             qs = qs.filter(tipo=tipo)
#         if lingua:
#             qs = qs.filter(lingua=lingua)

#         # Busca por título (se existir)
#         if busca:
#             qs = qs.filter(titulo__icontains=busca)

#         order_str = "+data" if ordem == "asc" else "-data"
#         qs = qs.order_by(order_str).skip(skip).limit(limit)

#         return [
#             {
#                 "id": str(aula.id),
#                 "tipo": aula.tipo,
#                 "lingua": aula.lingua,
#                 "data": aula.data.isoformat(),
#                 "creditos": aula.creditos,
#                 "titulo": getattr(aula, "titulo", None),
#                 "professor_id": str(aula.professor.id) if aula.professor else None,
#                 "professor_nome": getattr(aula.professor, "username", None) if aula.professor else None,
#                 "link_meet": getattr(aula, "link_meet", None),  # <<< incluído
#             }
#             for aula in qs
#         ]
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao listar aulas públicas: {str(e)}")

# @router.get("/minhas-reservas")
# def listar_reservas_aluno(request: Request):
#     """
#     Lista aulas em que o aluno autenticado está inscrito.
#     """
#     user = request.state.user
#     if user.get("is_professor"):
#         raise HTTPException(status_code=403, detail="Apenas alunos acessam suas reservas.")

#     try:
#         aluno_id = ObjectId(user["sub"])
#         qs = Aula.objects(alunos=aluno_id).order_by("+data")
#         return [
#             {
#                 "id": str(a.id),
#                 "tipo": a.tipo,
#                 "lingua": a.lingua,
#                 "data": a.data.isoformat(),
#                 "creditos": a.creditos,
#                 "titulo": getattr(a, "titulo", None),
#                 "professor_id": str(a.professor.id) if a.professor else None,
#                 "professor_nome": getattr(a.professor, "username", None) if a.professor else None,
#                 "link_meet": getattr(a, "link_meet", None),  # <<< incluído
#             }
#             for a in qs
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao buscar reservas: {str(e)}")
# use_cases/aula.py
from fastapi import APIRouter, HTTPException, Request, Query
from models.aula import Aula
from models.user import User
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from typing import Optional, List

router = APIRouter()

# ======== SCHEMAS ========

class AulaCreateRequest(BaseModel):
    titulo: Optional[str] = None
    tipo: str = Field(..., regex="^(particular|grupo)$")
    lingua: str = Field(..., regex="^(ingles|espanhol)$")
    data: datetime
    professor_id: str
    alunos_ids: List[str] = []
    link_meet: Optional[str] = None

class AulaUpdateRequest(BaseModel):
    titulo: Optional[str] = None
    tipo: Optional[str] = Field(None, regex="^(particular|grupo)$")
    lingua: Optional[str] = Field(None, regex="^(ingles|espanhol)$")
    data: Optional[datetime] = None
    link_meet: Optional[str] = None

# ======== HELPERS ========

def _get_user_or_404(user_id: str) -> User:
    try:
        return User.objects.get(id=ObjectId(user_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

def _get_aula_or_404(aula_id: str) -> Aula:
    try:
        return Aula.objects.get(id=ObjectId(aula_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Aula não encontrada.")

# ======== ROTAS ========

@router.post("/aulas")
def criar_aula(payload: AulaCreateRequest, request: Request):
    user = request.state.user
    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem criar aulas.")

    professor = _get_user_or_404(payload.professor_id)
    if str(professor.id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Você só pode criar aulas como você mesmo.")

    # Carrega alunos (se houver)
    alunos = []
    for aluno_id in payload.alunos_ids:
        aluno = _get_user_or_404(aluno_id)
        if getattr(aluno, "is_professor", False):
            raise HTTPException(status_code=400, detail="Um professor não pode ser aluno.")
        alunos.append(aluno)

    try:
        aula = Aula(
            titulo=payload.titulo,
            tipo=payload.tipo,
            lingua=payload.lingua,
            data=payload.data,
            professor=professor,
            alunos=alunos,
            link_meet=payload.link_meet,
        )
        aula.clean()  # seta 'creditos' e valida limites
        aula.save()
        return {"mensagem": "Aula criada com sucesso", "id": str(aula.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar aula: {str(e)}")

@router.patch("/aulas/{aula_id}")
def atualizar_aula(aula_id: str, payload: AulaUpdateRequest, request: Request):
    """
    Atualiza campos de uma aula (apenas do próprio professor).
    Se 'tipo' mudar, recalcule 'creditos' via clean().
    """
    user = request.state.user
    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem editar aulas.")

    aula = _get_aula_or_404(aula_id)

    if str(aula.professor.id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Você só pode editar suas próprias aulas.")

    # Aplica alterações
    if payload.titulo is not None:
        aula.titulo = payload.titulo.strip() or None
    if payload.tipo is not None:
        aula.tipo = payload.tipo
    if payload.lingua is not None:
        aula.lingua = payload.lingua
    if payload.data is not None:
        aula.data = payload.data
    if payload.link_meet is not None:
        aula.link_meet = payload.link_meet.strip() or None

    try:
        # Revalida (e recalcula créditos se necessário)
        aula.clean()
        aula.save()
        return {
            "mensagem": "Aula atualizada com sucesso",
            "aula": {
                "id": str(aula.id),
                "titulo": getattr(aula, "titulo", None),
                "tipo": aula.tipo,
                "lingua": aula.lingua,
                "data": aula.data.isoformat(),
                "creditos": aula.creditos,
                "link_meet": getattr(aula, "link_meet", None),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar aula: {str(e)}")

@router.delete("/aulas/{aula_id}")
def deletar_aula(aula_id: str, request: Request, repetir: Optional[bool] = Query(False)):
    """
    Deleta uma aula do professor autenticado.
    Parâmetro 'repetir' está disponível caso você venha a implementar séries/recorrência no modelo.
    Atualmente remove apenas a aula específica (ignora 'repetir').
    """
    user = request.state.user
    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem deletar aulas.")

    aula = _get_aula_or_404(aula_id)

    if str(aula.professor.id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Você só pode deletar aulas criadas por você.")

    try:
        aula.delete()
        # Caso no futuro você implemente série, retorne lista de IDs deletados.
        return {"mensagem": "Aula deletada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar aula: {str(e)}")

@router.get("/minhas-aulas")
def listar_aulas_professor(request: Request):
    user = request.state.user
    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem acessar suas aulas.")

    try:
        aulas = Aula.objects(professor=ObjectId(user["sub"])).order_by("+data")
        return [
            {
                "id": str(aula.id),
                "titulo": getattr(aula, "titulo", "Aula"),
                "data": aula.data.isoformat(),
                "tipo": aula.tipo,
                "lingua": aula.lingua,
                "creditos": aula.creditos,
                "link_meet": getattr(aula, "link_meet", None),
            }
            for aula in aulas
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar aulas: {str(e)}")

@router.get("/aulas-publicas")
def listar_aulas_publicas(request: Request):
    user = request.state.user
    if user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Professores não podem reservar aulas.")

    try:
        agora = datetime.utcnow()
        aulas = Aula.objects(data__gte=agora).order_by("+data")
        return [
            {
                "id": str(aula.id),
                "tipo": aula.tipo,
                "lingua": aula.lingua,
                "data": aula.data.isoformat(),
                "professor": str(aula.professor.id),
                "creditos": aula.creditos,
                "titulo": getattr(aula, "titulo", None),
                "link_meet": getattr(aula, "link_meet", None),
            }
            for aula in aulas
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar aulas: {str(e)}")

@router.post("/reservar/{aula_id}")
def reservar_aula(aula_id: str, request: Request):
    user = request.state.user
    if user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Professores não podem reservar aulas.")

    aula = _get_aula_or_404(aula_id)
    aluno = _get_user_or_404(user["sub"])

    if aluno in aula.alunos:
        raise HTTPException(status_code=400, detail="Você já está inscrito nesta aula.")
    if aula.tipo == "particular" and len(aula.alunos) >= 1:
        raise HTTPException(status_code=400, detail="Aula particular já está preenchida.")
    if aula.tipo == "grupo" and len(aula.alunos) >= 4:
        raise HTTPException(status_code=400, detail="Aula em grupo está cheia.")
    if aluno.creditos < aula.creditos:
        raise HTTPException(status_code=400, detail="Créditos insuficientes para reservar esta aula.")

    try:
        aluno.creditos -= aula.creditos
        aluno.save()
        aula.alunos.append(aluno)
        aula.save()
        return {
            "mensagem": "Reserva realizada com sucesso",
            "creditos_atualizados": aluno.creditos,
            "aula": {
                "id": str(aula.id),
                "titulo": getattr(aula, "titulo", None),
                "tipo": aula.tipo,
                "lingua": aula.lingua,
                "data": aula.data.isoformat(),
                "creditos": aula.creditos,
                "link_meet": getattr(aula, "link_meet", None),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reservar aula: {str(e)}")

@router.get("/aulas-publicas-sem-login")
def listar_aulas_publicas_sem_login(
    tipo: Optional[str] = Query(None, pattern="^(particular|grupo)$"),
    lingua: Optional[str] = Query(None, pattern="^(ingles|espanhol)$"),
    busca: Optional[str] = Query(None, description="Busca por título (case-insensitive)"),
    data_de: Optional[str] = Query(None, description="YYYY-MM-DDTHH:MM:SS"),
    data_ate: Optional[str] = Query(None, description="YYYY-MM-DDTHH:MM:SS"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    ordem: str = Query("asc", pattern="^(asc|desc)$"),
):
    try:
        qs = Aula.objects

        if data_de:
            try:
                dt = datetime.fromisoformat(data_de)
                qs = qs.filter(data__gte=dt)
            except Exception:
                raise HTTPException(status_code=400, detail="Parâmetro 'data_de' inválido (use ISO 8601).")
        if data_ate:
            try:
                dt = datetime.fromisoformat(data_ate)
                qs = qs.filter(data__lte=dt)
            except Exception:
                raise HTTPException(status_code=400, detail="Parâmetro 'data_ate' inválido (use ISO 8601).")

        if tipo:
            qs = qs.filter(tipo=tipo)
        if lingua:
            qs = qs.filter(lingua=lingua)
        if busca:
            qs = qs.filter(titulo__icontains=busca)

        order_str = "+data" if ordem == "asc" else "-data"
        qs = qs.order_by(order_str).skip(skip).limit(limit)

        return [
            {
                "id": str(aula.id),
                "tipo": aula.tipo,
                "lingua": aula.lingua,
                "data": aula.data.isoformat(),
                "creditos": aula.creditos,
                "titulo": getattr(aula, "titulo", None),
                "professor_id": str(aula.professor.id) if aula.professor else None,
                "professor_nome": getattr(aula.professor, "username", None) if aula.professor else None,
                "link_meet": getattr(aula, "link_meet", None),
            }
            for aula in qs
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar aulas públicas: {str(e)}")

@router.get("/minhas-reservas")
def listar_reservas_aluno(request: Request):
    user = request.state.user
    if user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas alunos acessam suas reservas.")

    try:
        aluno_id = ObjectId(user["sub"])
        qs = Aula.objects(alunos=aluno_id).order_by("+data")
        return [
            {
                "id": str(a.id),
                "tipo": a.tipo,
                "lingua": a.lingua,
                "data": a.data.isoformat(),
                "creditos": a.creditos,
                "titulo": getattr(a, "titulo", None),
                "professor_id": str(a.professor.id) if a.professor else None,
                "professor_nome": getattr(a.professor, "username", None) if a.professor else None,
                "link_meet": getattr(a, "link_meet", None),
            }
            for a in qs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar reservas: {str(e)}")


