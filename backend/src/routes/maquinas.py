# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from src.models.models import db, Maquina, TipoMaquinaEnum, TipoControleEnum, StatusMaquinaEnum
from datetime import datetime
# TODO: Importar decorator de autenticação/autorização
# from .auth import login_required, role_required # Exemplo

from functools import wraps

maquinas_bp = Blueprint("maquinas_bp", __name__)

# Decorator placeholder para simular verificação de role (substituir por real)
def role_required(role):
    def decorator(f):
        @wraps(f) # Preserva metadados da função original
        def decorated_function(*args, **kwargs):
            # Lógica de verificação de role (ex: verificar current_user.role)
            # Por agora, permite tudo para demonstração
            print(f"Verificando role: {role}") # Log de simulação
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota para criar uma nova máquina (Apenas Gestor)
@maquinas_bp.route("/maquinas", methods=["POST"])
# @login_required # Descomentar quando auth estiver pronto
@role_required("gestor") # Aplicar verificação de role
def create_maquina():
    data = request.get_json()
    try:
        nova_maquina = Maquina(
            tipo=TipoMaquinaEnum(data["tipo"]),
            numero_frota=data["numero_frota"],
            data_aquisicao=datetime.strptime(data["data_aquisicao"], "%Y-%m-%d").date(),
            tipo_controle=TipoControleEnum(data["tipo_controle"]),
            nome=data["nome"],
            marca=data.get("marca"), # Marca é opcional
            status=StatusMaquinaEnum(data.get("status", "ativo")) # Default para ativo
        )
        db.session.add(nova_maquina)
        db.session.commit()
        return jsonify({"message": "Máquina criada com sucesso", "id": nova_maquina.id}), 201
    except KeyError as e:
        return jsonify({"message": f"Campo obrigatório ausente: {e}"}), 400
    except ValueError as e:
        return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao criar máquina: {e}"}), 500

# Rota para listar todas as máquinas (Gestor, Mecânico, Administrador)
@maquinas_bp.route("/maquinas", methods=["GET"])
# @login_required
def get_maquinas():
    try:
        # Adicionar filtros aqui se necessário (ex: por status, tipo)
        maquinas = Maquina.query.all()
        output = []
        for maquina in maquinas:
            maquina_data = {
                "id": maquina.id,
                "tipo": maquina.tipo.value,
                "numero_frota": maquina.numero_frota,
                "data_aquisicao": maquina.data_aquisicao.isoformat(),
                "tipo_controle": maquina.tipo_controle.value,
                "nome": maquina.nome,
                "marca": maquina.marca,
                "status": maquina.status.value
            }
            output.append(maquina_data)
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar máquinas: {e}"}), 500

# Rota para buscar uma máquina específica (Gestor, Mecânico, Administrador)
@maquinas_bp.route("/maquinas/<int:id>", methods=["GET"])
# @login_required
def get_maquina(id):
    try:
        maquina = Maquina.query.get_or_404(id)
        maquina_data = {
            "id": maquina.id,
            "tipo": maquina.tipo.value,
            "numero_frota": maquina.numero_frota,
            "data_aquisicao": maquina.data_aquisicao.isoformat(),
            "tipo_controle": maquina.tipo_controle.value,
            "nome": maquina.nome,
            "marca": maquina.marca,
            "status": maquina.status.value
        }
        return jsonify(maquina_data), 200
    except Exception as e:
         return jsonify({"message": f"Erro ao buscar máquina: {e}"}), 500

# Rota para atualizar uma máquina (Apenas Gestor)
@maquinas_bp.route("/maquinas/<int:id>", methods=["PUT"])
# @login_required
@role_required("gestor")
def update_maquina(id):
    data = request.get_json()
    maquina = Maquina.query.get_or_404(id)

    try:
        if "tipo" in data: maquina.tipo = TipoMaquinaEnum(data["tipo"])
        if "numero_frota" in data: maquina.numero_frota = data["numero_frota"]
        if "data_aquisicao" in data: maquina.data_aquisicao = datetime.strptime(data["data_aquisicao"], "%Y-%m-%d").date()
        if "tipo_controle" in data: maquina.tipo_controle = TipoControleEnum(data["tipo_controle"])
        if "nome" in data: maquina.nome = data["nome"]
        if "marca" in data: maquina.marca = data["marca"]
        if "status" in data: maquina.status = StatusMaquinaEnum(data["status"])

        db.session.commit()
        return jsonify({"message": "Máquina atualizada com sucesso"}), 200
    except ValueError as e:
        return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao atualizar máquina: {e}"}), 500

# Rota para deletar uma máquina (Apenas Gestor) - ou inativar?
# A especificação pede para inativar, então PUT para status=inativo é mais adequado.
# Se a deleção for realmente necessária, descomentar abaixo.
# @maquinas_bp.route("/maquinas/<int:id>", methods=["DELETE"])
# @login_required
# @role_required("gestor")
# def delete_maquina(id):
#     try:
#         maquina = Maquina.query.get_or_404(id)
#         # Verificar se há manutenções associadas antes de deletar?
#         db.session.delete(maquina)
#         db.session.commit()
#         return jsonify({"message": "Máquina deletada com sucesso"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": f"Erro ao deletar máquina: {e}"}), 500

