# -*- coding: utf-8 -*-
import logging
from flask import Blueprint, request, jsonify
from src.models.models import db, Manutencao, Maquina, TipoManutencaoEnum, CategoriaServicoEnum
from datetime import datetime
from functools import wraps

manutencoes_bp = Blueprint("manutencoes_bp", __name__)

# Decorator placeholder para simular verificação de role (substituir por real)
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Lógica de verificação de role (ex: verificar current_user.role)
            print(f"Verificando role: {role}")  # Log de simulação
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota para criar uma nova manutenção (Gestor, Mecânico)
@manutencoes_bp.route("/manutencoes", methods=["POST"])
# @login_required
# @role_required(["gestor", "mecanico"])
def create_manutencao():
    data = request.get_json() or {}
    errors = {}
    try:
        # Validação e conversão de campos
        maquina_id = data.get("Maquina_id")
        if not maquina_id:
            errors["Maquina_id"] = "Máquina é obrigatória."
        else:
            maquina = Maquina.query.get(maquina_id)
            if not maquina:
                errors["maquina_id"] = "Máquina não encontrada."

        horimetro_hodometro_val = data.get("horimetro_hodometro")
        try:
            horimetro_hodometro = float(horimetro_hodometro_val)
        except (TypeError, ValueError):
            errors["horimetro_hodometro"] = "Valor inválido para Horímetro/Hodômetro."

        data_entrada_str = data.get("data_entrada")
        try:
            data_entrada = datetime.fromisoformat(data_entrada_str.replace("Z", "+00:00")
                                                   if data_entrada_str.endswith("Z") else data_entrada_str)
        except Exception:
            errors["data_entrada"] = "Formato inválido para Data de Entrada."

        data_saida = None
        data_saida_str = data.get("data_saida")
        if data_saida_str:
            try:
                data_saida = datetime.fromisoformat(data_saida_str.replace("Z", "+00:00")
                                                   if data_saida_str.endswith("Z") else data_saida_str)
            except Exception:
                errors["data_saida"] = "Formato inválido para Data de Saída."

        tipo_manutencao = None
        tipo_str = data.get("tipo_manutencao")
        try:
            tipo_manutencao = TipoManutencaoEnum(tipo_str)
        except Exception:
            errors["tipo_manutencao"] = "Valor inválido para Tipo de Manutenção."

        categoria_servico = None
        categoria_str = data.get("categoria_servico")
        try:
            categoria_servico = CategoriaServicoEnum(categoria_str)
        except Exception:
            errors["categoria_servico"] = "Valor inválido para Categoria do Serviço."

        responsavel_servico = data.get("responsavel_servico")
        if not responsavel_servico:
            errors["responsavel_servico"] = "Responsável pelo Serviço é obrigatório."

        custo = None
        custo_str = data.get("custo")
        if custo_str is not None:
            try:
                custo = float(custo_str)
            except Exception:
                errors["custo"] = "Valor inválido para Custo."

        comentario = data.get("comentario")

        if errors:
            return jsonify({"message": "Erro de validação", "errors": errors}), 400

        nova = Manutencao(
            maquina_id=maquina_id,
            horimetro_hodometro=horimetro_hodometro,
            data_entrada=data_entrada,
            data_saida=data_saida,
            tipo_manutencao=tipo_manutencao,
            categoria_servico=categoria_servico,
            categoria_outros_especificacao=data.get("categoria_outros_especificacao"),
            comentario=comentario,
            responsavel_servico=responsavel_servico,
            custo=custo
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify({"message": "Manutenção registrada com sucesso", "id": nova.id}), 201

    except Exception as e:
        db.session.rollback()
        logging.exception("Erro interno ao criar manutenção")
        return jsonify({"message": "Erro interno ao registrar manutenção. Contate o suporte."}), 500

# Rota para listar manutenções (com filtros)
@manutencoes_bp.route("/manutencoes", methods=["GET"])
def get_manutencoes():
    try:
        query = Manutencao.query
        if "maquina_id" in request.args:
            query = query.filter_by(maquina_id=request.args.get("maquina_id"))
        if "tipo_manutencao" in request.args:
            query = query.filter(Manutencao.tipo_manutencao == TipoManutencaoEnum(request.args.get("tipo_manutencao")))
        if "start_date" in request.args and "end_date" in request.args:
            sd = datetime.fromisoformat(request.args.get("start_date"))
            ed = datetime.fromisoformat(request.args.get("end_date"))
            query = query.filter(Manutencao.data_entrada.between(sd, ed))
        muts = query.order_by(Manutencao.data_entrada.desc()).all()
        result = [
            {
                "id": m.id,
                "maquina_id": m.maquina_id,
                "maquina_nome": m.maquina.nome,
                "horimetro_hodometro": m.horimetro_hodometro,
                "data_entrada": m.data_entrada.isoformat(),
                "data_saida": m.data_saida.isoformat() if m.data_saida else None,
                "tipo_manutencao": m.tipo_manutencao.value,
                "categoria_servico": m.categoria_servico.value,
                "categoria_outros_especificacao": m.categoria_outros_especificacao,
                "comentario": m.comentario,
                "responsavel_servico": m.responsavel_servico,
                "custo": m.custo
            }
            for m in muts
        ]
        return jsonify(result), 200
    except Exception:
        logging.exception("Erro ao buscar manutenções")
        return jsonify({"message": "Erro ao buscar manutenções"}), 500

# Rota para buscar uma manutenção específica
@manutencoes_bp.route("/manutencoes/<int:id>", methods=["GET"])
def get_manutencao(id):
    try:
        m = Manutencao.query.get_or_404(id)
        data = {
            "id": m.id,
            "maquina_id": m.maquina_id,
            "maquina_nome": m.maquina.nome,
            "horimetro_hodometro": m.horimetro_hodometro,
            "data_entrada": m.data_entrada.isoformat(),
            "data_saida": m.data_saida.isoformat() if m.data_saida else None,
            "tipo_manutencao": m.tipo_manutencao.value,
            "categoria_servico": m.categoria_servico.value,
            "categoria_outros_especificacao": m.categoria_outros_especificacao,
            "comentario": m.comentario,
            "responsavel_servico": m.responsavel_servico,
            "custo": m.custo
        }
        return jsonify(data), 200
    except Exception:
        logging.exception("Erro ao buscar manutenção específica")
        return jsonify({"message": "Erro ao buscar manutenção"}), 500

# Rota para atualizar uma manutenção (Apenas Gestor)
@manutencoes_bp.route("/manutencoes/<int:id>", methods=["PUT"])
def update_manutencao(id):
    data = request.get_json() or {}
    m = Manutencao.query.get_or_404(id)
    # Atualiza campos permitidos dinamicamente
    try:
        # Campos simples
        for field in ["horimetro_hodometro", "data_entrada", "data_saida", "comentario", "responsavel_servico", "custo"]:
            if field in data:
                setattr(m, field, data[field])

        # Enum: tipo_manutencao
        if "tipo_manutencao" in data:
            try:
                m.tipo_manutencao = TipoManutencaoEnum(data["tipo_manutencao"])
            except ValueError:
                return jsonify({"message": f"Tipo de manutenção inválido: {data['tipo_manutencao']}"}), 400

        # Enum: categoria_servico
        if "categoria_servico" in data:
            try:
                m.categoria_servico = CategoriaServicoEnum(data["categoria_servico"])
            except ValueError:
                return jsonify({"message": f"Categoria de serviço inválida: {data['categoria_servico']}"}), 400

        db.session.commit()
        return jsonify({"message": "Manutenção atualizada com sucesso"}), 200

    except Exception:
        db.session.rollback()
        logging.exception("Erro ao atualizar manutenção")
        return jsonify({"message": "Erro ao atualizar manutenção"}), 500

# Rota para excluir uma manutenção
@manutencoes_bp.route("/manutencoes/<int:id>", methods=["DELETE"])
@role_required("gestor")
def delete_manutencao(id):
    try:
        m = Manutencao.query.get_or_404(id)
        db.session.delete(m)
        db.session.commit()
        return jsonify({"message": "Manutenção excluída com sucesso"}), 200
    except Exception:
        db.session.rollback()
        logging.exception("Erro ao excluir manutenção")
        return jsonify({"message": "Erro ao excluir manutenção"}), 500