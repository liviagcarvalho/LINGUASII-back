# use_cases/aula.py

from fastapi import APIRouter, HTTPException, Request
from models.aula import Aula
from models.user import User
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from fastapi import Path

router = APIRouter()

class AulaCreateRequest(BaseModel):
    tipo: str = Field(..., regex="^(particular|grupo)$")
    lingua: str = Field(..., regex="^(ingles|espanhol)$")
    data: datetime
    professor_id: str
    alunos_ids: list[str] = []  # default vazio
    imagem: str | None = None


@router.post("/aulas")
def criar_aula(payload: AulaCreateRequest, request: Request):
    user = request.state.user

    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem criar aulas.")

    # Buscar professor
    try:
        professor = User.objects.get(id=ObjectId(payload.professor_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")

    # Verificar se quem está autenticado é o mesmo que está tentando criar a aula
    if str(professor.id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Você só pode criar aulas como você mesmo.")

    # Buscar alunos
    # Buscar alunos 
    alunos = []
    for aluno_id in payload.alunos_ids:
        try:
            aluno = User.objects.get(id=ObjectId(aluno_id))
            if aluno.is_professor:
                raise HTTPException(status_code=400, detail="Um professor não pode ser aluno.")
            alunos.append(aluno)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Aluno com ID {aluno_id} não encontrado.")


    # Criar e salvar a aula
    try:
        aula = Aula(
            tipo=payload.tipo,
            lingua=payload.lingua,
            data=payload.data,
            professor=professor,
            alunos=alunos,
            imagem=payload.imagem,
        )
        aula.clean()  # aplica regras (valida nº de alunos e define créditos)
        aula.save()

        return {"mensagem": "Aula criada com sucesso", "id": str(aula.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar aula: {str(e)}")

@router.delete("/aulas/{aula_id}")
def deletar_aula(aula_id: str, request: Request):
    user = request.state.user

    if not user.get("is_professor"):
        raise HTTPException(status_code=403, detail="Apenas professores podem deletar aulas.")

    try:
        aula = Aula.objects.get(id=ObjectId(aula_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Aula não encontrada.")

    # Verifica se o professor logado é o criador da aula
    if str(aula.professor.id) != user["sub"]:
        raise HTTPException(status_code=403, detail="Você só pode deletar aulas criadas por você.")

    try:
        aula.delete()
        return {"mensagem": "Aula deletada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar aula: {str(e)}")
