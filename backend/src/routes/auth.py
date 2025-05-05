# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
# TODO: Implement JWT or Flask-Login for session management
# from flask_login import login_user, logout_user, login_required, current_user
from src.models.models import db, Usuario, RoleEnum

import logging

# Blueprint de autenticação
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")
# Habilita CORS para todas as rotas deste blueprint
CORS(
    auth_bp,
    resources={r"/api/auth/*": {"origins": "https://laufoficina.vercel.app"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

logging.basicConfig(level=logging.INFO)

# Rota de Login
@auth_bp.route("/login", methods=["OPTIONS", "POST"])
def login():
    # Responde à preflight
    if request.method == "OPTIONS":
        return make_response(("", 204, {
            "Access-Control-Allow-Origin": "https://laufoficina.vercel.app",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        }))

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
        if not check_password_hash(user.password_hash, password):
            logging.warning(f"Senha incorreta para o usuário {username}")
            return jsonify({"message": "Credenciais inválidas"}), 401

        # TODO: Gerar token JWT ou usar flask_login.login_user(user)
        logging.info(f"Login bem-sucedido para usuário: {username}")
        return jsonify({"message": "Login bem-sucedido", "user_id": user.id, "role": user.role.value}), 200
    except Exception as e:
        logging.error(f"Erro inesperado durante o login: {e}", exc_info=True)
        return jsonify({"message": "Erro interno no servidor"}), 500

# Rota de Logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # TODO: Invalidar token JWT ou usar flask_login.logout_user()
    return jsonify({'message': 'Logout bem-sucedido'}), 200

# Rota de registro de usuário inicial (ex: admin/gestor)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role_str = data.get('role', 'mecanico')

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

# Rota para checar autenticação
@auth_bp.route("/check", methods=["GET"])
def check_auth():
    return jsonify({"authenticated": True}), 200
