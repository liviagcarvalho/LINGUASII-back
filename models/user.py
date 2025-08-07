from mongoengine import * # Importa o MongoEngine para trabalhar com o MongoDB

# models/user.py

class User(Document):
    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    nome = StringField(required=True)
    senha = StringField(required=True)
    is_professor = BooleanField(default=False)
    creditos = IntField(default=0)  # Novo campo adicionado

    meta = {
        "collection": "users"
    }

