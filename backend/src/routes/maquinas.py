from flask import Blueprint, request, jsonify, abort
from src.models.models import db, Maquina, TipoMaquinaEnum, TipoControleEnum, StatusMaquinaEnum
from datetime import datetime
from functools import wraps

maquinas_bp = Blueprint("maquinas_bp", __name__)

# Decorator placeholder para simular verificação de role (substituir por real)
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Verificando role: {role}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota unificada para criar e listar máquinas
@maquinas_bp.route("/maquinas", methods=["GET", "POST"])
@role_required("gestor")
def handle_maquinas():
    if request.method == "POST":
        data = request.get_json() or {}
        try:
            nova_maquina = Maquina(
                tipo=TipoMaquinaEnum(data["tipo"]),
                numero_frota=data["numero_frota"],
                data_aquisicao=datetime.strptime(data["data_aquisicao"], "%Y-%m-%d").date(),
                tipo_controle=TipoControleEnum(data["tipo_controle"]),
                nome=data["nome"],
                marca=data.get("marca"),
                status=StatusMaquinaEnum(data.get("status", "ativo"))
            )
            db.session.add(nova_maquina)
            db.session.commit()
            return jsonify({"message": "Máquina criada com sucesso", "id": nova_maquina.id}), 201
        except KeyError as e:
            return jsonify({"message": f"Campo obrigatório ausente: {e.args[0]}"}), 400
        except ValueError as e:
            return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Erro ao criar máquina: {e}"}), 500
    # GET
    try:
        maquinas = Maquina.query.all()
        output = []
        for maquina in maquinas:
            output.append({
                "id": maquina.id,
                "tipo": maquina.tipo.value,
                "numero_frota": maquina.numero_frota,
                "data_aquisicao": maquina.data_aquisicao.isoformat(),
                "tipo_controle": maquina.tipo_controle.value,
                "nome": maquina.nome,
                "marca": maquina.marca,
                "status": maquina.status.value
            })
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar máquinas: {e}"}), 500

# Rota para operações CRUD em máquina específica
@maquinas_bp.route("/maquinas/<int:maquina_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@role_required("gestor")
def handle_maquina(maquina_id):
    maquina = Maquina.query.get_or_404(maquina_id)
    # GET detalhe
    if request.method == "GET":
        return jsonify({
            "id": maquina.id,
            "tipo": maquina.tipo.value,
            "numero_frota": maquina.numero_frota,
            "data_aquisicao": maquina.data_aquisicao.isoformat(),
            "tipo_controle": maquina.tipo_controle.value,
            "nome": maquina.nome,
            "marca": maquina.marca,
            "status": maquina.status.value
        }), 200

    # PUT/PATCH para atualizar
    if request.method in ("PUT", "PATCH"):
        data = request.get_json() or {}
        try:
            if "tipo" in data:
                maquina.tipo = TipoMaquinaEnum(data["tipo"])
            if "numero_frota" in data:
                maquina.numero_frota = data["numero_frota"]
            if "data_aquisicao" in data:
                maquina.data_aquisicao = datetime.strptime(data["data_aquisicao"], "%Y-%m-%d").date()
            if "tipo_controle" in data:
                maquina.tipo_controle = TipoControleEnum(data["tipo_controle"])
            if "nome" in data:
                maquina.nome = data["nome"]
            if "marca" in data:
                maquina.marca = data.get("marca")
            if "status" in data:
                maquina.status = StatusMaquinaEnum(data.get("status"))
            db.session.commit()
            return jsonify({"message": "Máquina atualizada com sucesso"}), 200
        except ValueError as e:
            return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Erro ao atualizar máquina: {e}"}), 500

    # DELETE para remover
    if request.method == "DELETE":
        try:
            db.session.delete(maquina)
            db.session.commit()
            return jsonify({"message": "Máquina removida com sucesso"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Erro ao excluir máquina: {e}"}), 500

    # Método não permitido
    abort(405)