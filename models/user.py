from mongoengine import * # Importa o MongoEngine para trabalhar com o MongoDB

# models/user.py

class User(Document):
    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    nome = StringField(required=True)
    senha = StringField(required=True)  # você pode futuramente fazer hash
    is_professor = BooleanField(default=False)

    meta = {
        "collection": "users"  # Nome da coleção no MongoDB
    }
