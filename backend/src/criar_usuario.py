from src.main import app
from src.models.models import db, Usuario, RoleEnum
from werkzeug.security import generate_password_hash

# Configura os dados do novo usuário
username = "admin"
senha = "1234"
role = RoleEnum.GESTOR

with app.app_context():
    senha_hash = generate_password_hash(senha)
    
    # Verifica se já existe
    usuario_existente = Usuario.query.filter_by(username=username).first()
    if usuario_existente:
        print("Usuário já existe.")
    else:
        novo_usuario = Usuario(
            username=username,
            password_hash=senha_hash,
            role=role
        )
        db.session.add(novo_usuario)
        db.session.commit()
        print("Usuário criado com sucesso.")