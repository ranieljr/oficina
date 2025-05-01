# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
# TODO: Implement JWT or Flask-Login for session management
# from flask_login import login_user, logout_user, login_required, current_user
from src.models.models import db, Usuario, RoleEnum

import logging

auth_bp = Blueprint("auth_bp", __name__)

logging.basicConfig(level=logging.INFO)

# Rota de Login (Placeholder - precisa de implementação de sessão/token)
@auth_bp.route("/login", methods=["POST"])
def login():
    logging.info("Recebida requisição de login")
    try:
        data = request.get_json()
        if not data:
            logging.warning("Requisição de login sem corpo JSON")
            return jsonify({"message": "Corpo da requisição inválido"}), 400
        
        username = data.get("username")
        password = data.get("password")
        logging.info(f"Tentativa de login para usuário: {username}")

        if not username or not password:
            logging.warning("Nome de usuário ou senha ausentes na requisição")
            return jsonify({"message": "Nome de usuário e senha são obrigatórios"}), 400

        user = Usuario.query.filter_by(username=username).first()

        if not user:
            logging.warning(f"Usuário '{username}' não encontrado no banco de dados")
            return jsonify({"message": "Credenciais inválidas"}), 401
        
        logging.info(f"Usuário {username} encontrado. Verificando senha...")
        password_check_result = check_password_hash(user.password_hash, password)
        logging.info(f"Resultado da verificação de senha para {username}: {password_check_result}")

        if not password_check_result:
            logging.warning(f"Senha incorreta para o usuário {username}")
            return jsonify({"message": "Credenciais inválidas"}), 401

        # TODO: Gerar token JWT ou usar flask_login.login_user(user)
        logging.info(f"Login bem-sucedido para usuário: {username}")
        # Exemplo simples de retorno (sem token real):
        return jsonify({"message": "Login bem-sucedido", "user_id": user.id, "role": user.role.value}), 200
    except Exception as e:
        logging.error(f"Erro inesperado durante o login: {e}", exc_info=True)
        return jsonify({"message": "Erro interno no servidor"}), 500

# Rota de Logout (Placeholder)
@auth_bp.route('/logout', methods=['POST'])
# @login_required # Descomentar quando usar Flask-Login
def logout():
    # TODO: Invalidar token JWT ou usar flask_login.logout_user()
    return jsonify({'message': 'Logout bem-sucedido'}), 200

# Rota para criar um usuário inicial (ex: admin/gestor) - pode ser removida ou protegida depois
@auth_bp.route('/register', methods=['POST'])
def register():
    # Idealmente, esta rota deve ser protegida ou usada apenas para setup inicial
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role_str = data.get('role', 'mecanico') # Default para mecanico se não especificado

    if not username or not password:
        return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({'message': 'Nome de usuário já existe'}), 409

    try:
        role = RoleEnum(role_str)
    except ValueError:
        return jsonify({'message': f'Role inválido: {role_str}. Roles válidos: {[r.value for r in RoleEnum]}' }), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = Usuario(username=username, password_hash=hashed_password, role=role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário criado com sucesso'}), 201

