# models/aula.py
from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    ReferenceField,
    ListField,
    IntField,
    ValidationError,
)
from models.user import User

class Aula(Document):
    tipo = StringField(required=True, choices=["particular", "grupo"])
    lingua = StringField(required=True, choices=["ingles", "espanhol"])
    data = DateTimeField(required=True)
    professor = ReferenceField(User, required=True)
    alunos = ListField(ReferenceField(User), required=False, max_length=4)
    creditos = IntField(required=True)
    link_meet = StringField()  # <<< novo campo
    # imagem REMOVIDA

    def clean(self):
        # Permitir aulas sem alunos na criação
        if self.alunos:
            if self.tipo == "particular" and len(self.alunos) != 1:
                raise ValidationError("Aula particular deve ter exatamente 1 aluno.")
            elif self.tipo == "grupo" and not (1 <= len(self.alunos) <= 4):
                raise ValidationError("Aula em grupo deve ter entre 1 e 4 alunos.")

        # Define automaticamente os créditos conforme o tipo
        if self.tipo == "particular":
            self.creditos = 3
        elif self.tipo == "grupo":
            self.creditos = 1

    meta = {
        "collection": "aulas",
        "strict": False,  # ignora campos extras nos docs antigos
    }
