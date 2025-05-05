# Substituir o conteúdo do from flask import Blueprint, request, jsonify
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
        data = request.get_json()
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
            return jsonify({"message": f"Campo obrigatório ausente: {e}"}), 400
        except ValueError as e:
            return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Erro ao criar máquina: {e}"}), 500
    else:
        try:
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
