# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from src.models.models import db, Manutencao, Maquina, TipoManutencaoEnum, CategoriaServicoEnum
from datetime import datetime
from functools import wraps
# TODO: Importar decorator de autenticação/autorização
# from .auth import login_required, role_required # Exemplo

manutencoes_bp = Blueprint("manutencoes_bp", __name__)

# Decorator placeholder para simular verificação de role (substituir por real)
def role_required(role):
    def decorator(f):
        # @wraps(f) # Usar se importar wraps de functools
        def decorated_function(*args, **kwargs):
            # Lógica de verificação de role (ex: verificar current_user.role)
            # Por agora, permite tudo para demonstração
            print(f"Verificando role: {role}") # Log de simulação
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rota para criar uma nova manutenção (Gestor, Mecânico)
@manutencoes_bp.route("/manutencoes", methods=["POST"])
# @login_required
# @role_required(["gestor", "mecanico"]) # Permitir gestor e mecânico
def create_manutencao():
    data = request.get_json()
    errors = {}
    try:
        # Validação e conversão de campos
        maquina_id = data.get("maquina_id")
        if not maquina_id:
            errors["maquina_id"] = "Máquina é obrigatória."
        else:
            maquina = Maquina.query.get(maquina_id)
            if not maquina:
                errors["maquina_id"] = "Máquina não encontrada."

        horimetro_hodometro_str = data.get("horimetro_hodometro")
        horimetro_hodometro = None
        if not horimetro_hodometro_str:
            errors["horimetro_hodometro"] = "Horímetro/Hodômetro é obrigatório."
        else:
            try:
                horimetro_hodometro = float(horimetro_hodometro_str) # Usar float para permitir decimais se necessário
            except (ValueError, TypeError):
                errors["horimetro_hodometro"] = "Valor inválido para Horímetro/Hodômetro."

        data_entrada_str = data.get("data_entrada")
        data_entrada = None
        if not data_entrada_str:
            errors["data_entrada"] = "Data de Entrada é obrigatória."
        else:
            try:
                # Tentativa de parse robusta para ISO 8601 (com ou sem Z, com ou sem milissegundos)
                data_entrada_str_cleaned = data_entrada_str.replace("Z", "+00:00") if data_entrada_str.endswith("Z") else data_entrada_str
                data_entrada = datetime.fromisoformat(data_entrada_str_cleaned)

            except (ValueError, TypeError):
                errors["data_entrada"] = "Formato inválido para Data de Entrada."

        data_saida_str = data.get("data_saida")
        data_saida = None
        if data_saida_str:
            try:
                # Tentativa de parse robusta para ISO 8601 (com ou sem Z, com ou sem milissegundos)
                data_saida_str_cleaned = data_saida_str.replace("Z", "+00:00") if data_saida_str.endswith("Z") else data_saida_str
                data_saida = datetime.fromisoformat(data_saida_str_cleaned)

            except (ValueError, TypeError):
                 errors["data_saida"] = "Formato inválido para Data de Saída."

        tipo_manutencao_str = data.get("tipo_manutencao")
        tipo_manutencao = None
        if not tipo_manutencao_str:
            errors["tipo_manutencao"] = "Tipo de Manutenção é obrigatório."
        else:
            try:
                tipo_manutencao = TipoManutencaoEnum(tipo_manutencao_str)
            except ValueError:
                errors["tipo_manutencao"] = "Valor inválido para Tipo de Manutenção."

        categoria_servico_str = data.get("categoria_servico")
        categoria_servico = None
        categoria_outros_especificacao = None
        if not categoria_servico_str:
            errors["categoria_servico"] = "Categoria do Serviço é obrigatória."
        else:
            try:
                categoria_servico = CategoriaServicoEnum(categoria_servico_str)
                if categoria_servico == CategoriaServicoEnum.OUTROS:
                    categoria_outros_especificacao = data.get("categoria_outros_especificacao")
                    # Poderia adicionar validação se a especificação é obrigatória quando "Outros" é selecionado
            except ValueError:
                errors["categoria_servico"] = "Valor inválido para Categoria do Serviço."

        responsavel_servico = data.get("responsavel_servico")
        if not responsavel_servico:
            errors["responsavel_servico"] = "Responsável pelo Serviço é obrigatório."

        custo_str = data.get("custo")
        custo = None
        if custo_str is not None and custo_str != "": # Permitir custo zero ou vazio
            try:
                custo = float(custo_str)
            except (ValueError, TypeError):
                errors["custo"] = "Valor inválido para Custo."

        comentario = data.get("comentario") # Comentário é opcional

        if errors:
            return jsonify({"message": "Erro de validação", "errors": errors}), 400

        # Criação do objeto Manutencao se não houver erros
        nova_manutencao = Manutencao(
            maquina_id=maquina_id,
            horimetro_hodometro=horimetro_hodometro,
            data_entrada=data_entrada,
            data_saida=data_saida,
            tipo_manutencao=tipo_manutencao,
            categoria_servico=categoria_servico,
            categoria_outros_especificacao=categoria_outros_especificacao,
            comentario=comentario,
            responsavel_servico=responsavel_servico,
            custo=custo
        )
        db.session.add(nova_manutencao)
        db.session.commit()
        return jsonify({"message": "Manutenção registrada com sucesso", "id": nova_manutencao.id}), 201

    except Exception as e:
        db.session.rollback()
        # Logar o erro real para depuração interna
        print(f"Erro inesperado ao registrar manutenção: {e}")
        return jsonify({"message": f"Erro interno ao registrar manutenção. Contate o suporte."}), 500

# Rota para listar manutenções (com filtros) (Gestor, Mecânico, Administrador)
@manutencoes_bp.route("/manutencoes", methods=["GET"])
# @login_required
def get_manutencoes():
    try:
        query = Manutencao.query

        # Filtros (exemplos)
        if "maquina_id" in request.args:
            query = query.filter(Manutencao.maquina_id == request.args.get("maquina_id"))
        if "tipo_manutencao" in request.args:
            query = query.filter(Manutencao.tipo_manutencao == TipoManutencaoEnum(request.args.get("tipo_manutencao")))
        if "start_date" in request.args and "end_date" in request.args:
            start_date = datetime.strptime(request.args.get("start_date"), "%Y-%m-%d")
            end_date = datetime.strptime(request.args.get("end_date"), "%Y-%m-%d")
            query = query.filter(Manutencao.data_entrada.between(start_date, end_date))
        # Adicionar mais filtros conforme necessário (status, categoria, etc.)

        manutencoes = query.order_by(Manutencao.data_entrada.desc()).all()
        output = []
        for manutencao in manutencoes:
            manutencao_data = {
                "id": manutencao.id,
                "maquina_id": manutencao.maquina_id,
                "maquina_nome": manutencao.maquina.nome, # Incluir nome da máquina para conveniência
                "horimetro_hodometro": manutencao.horimetro_hodometro,
                "data_entrada": manutencao.data_entrada.isoformat(),
                "data_saida": manutencao.data_saida.isoformat() if manutencao.data_saida else None,
                "tipo_manutencao": manutencao.tipo_manutencao.value,
                "categoria_servico": manutencao.categoria_servico.value,
                "categoria_outros_especificacao": manutencao.categoria_outros_especificacao,
                "comentario": manutencao.comentario,
                "responsavel_servico": manutencao.responsavel_servico,
                "custo": manutencao.custo
            }
            output.append(manutencao_data)
        return jsonify(output), 200
    except ValueError as e: # Captura erro de enum inválido no filtro
        return jsonify({"message": f"Valor de filtro inválido: {e}"}), 400
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar manutenções: {e}"}), 500

# Rota para buscar uma manutenção específica (Gestor, Mecânico, Administrador)
@manutencoes_bp.route("/manutencoes/<int:id>", methods=["GET"])
# @login_required
def get_manutencao(id):
    try:
        manutencao = Manutencao.query.get_or_404(id)
        manutencao_data = {
            "id": manutencao.id,
            "maquina_id": manutencao.maquina_id,
            "maquina_nome": manutencao.maquina.nome,
            "horimetro_hodometro": manutencao.horimetro_hodometro,
            "data_entrada": manutencao.data_entrada.isoformat(),
            "data_saida": manutencao.data_saida.isoformat() if manutencao.data_saida else None,
            "tipo_manutencao": manutencao.tipo_manutencao.value,
            "categoria_servico": manutencao.categoria_servico.value,
            "categoria_outros_especificacao": manutencao.categoria_outros_especificacao,
            "comentario": manutencao.comentario,
            "responsavel_servico": manutencao.responsavel_servico,
            "custo": manutencao.custo
        }
        return jsonify(manutencao_data), 200
    except Exception as e:
         return jsonify({"message": f"Erro ao buscar manutenção: {e}"}), 500

# Rota para atualizar uma manutenção (Apenas Gestor)
@manutencoes_bp.route("/manutencoes/<int:id>", methods=["PUT"])
# @login_required
@role_required("gestor")
def update_manutencao(id):
    data = request.get_json()
    manutencao = Manutencao.query.get_or_404(id)

    try:
        # Atualizar campos permitidos
        if "horimetro_hodometro" in data: manutencao.horimetro_hodometro = data["horimetro_hodometro"]
        if "data_entrada" in data and data["data_entrada"]:
            data_entrada_str = data["data_entrada"]
            data_entrada_str_cleaned = data_entrada_str.replace("Z", "+00:00") if data_entrada_str.endswith("Z") else data_entrada_str
            manutencao.data_entrada = datetime.fromisoformat(data_entrada_str_cleaned)

        if "data_saida" in data:
            data_saida_str = data["data_saida"]
            if data_saida_str:
                data_saida_str_cleaned = data_saida_str.replace("Z", "+00:00") if data_saida_str.endswith("Z") else data_saida_str
                manutencao.data_saida = datetime.fromisoformat(data_saida_str_cleaned)
            else:
                manutencao.data_saida = None

        if "tipo_manutencao" in data: manutencao.tipo_manutencao = TipoManutencaoEnum(data["tipo_manutencao"])
        if "categoria_servico" in data:
            cat_servico = CategoriaServicoEnum(data["categoria_servico"])
            manutencao.categoria_servico = cat_servico
            if cat_servico == CategoriaServicoEnum.OUTROS and "categoria_outros_especificacao" in data:
                manutencao.categoria_outros_especificacao = data["categoria_outros_especificacao"]
            elif cat_servico != CategoriaServicoEnum.OUTROS:
                 manutencao.categoria_outros_especificacao = None # Limpa se não for mais Outros
        if "comentario" in data: manutencao.comentario = data["comentario"]
        if "responsavel_servico" in data: manutencao.responsavel_servico = data["responsavel_servico"]
        if "custo" in data: manutencao.custo = data["custo"]

        db.session.commit()
        return jsonify({"message": "Manutenção atualizada com sucesso"}), 200
    except ValueError as e:
        return jsonify({"message": f"Valor inválido fornecido: {e}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao atualizar manutenção: {e}"}), 500

# Rota para buscar histórico de manutenções por máquina (Gestor, Mecânico, Administrador)
@manutencoes_bp.route("/maquinas/<int:maquina_id>/manutencoes", methods=["GET"])
# @login_required
def get_manutencoes_por_maquina(maquina_id):
    try:
        Maquina.query.get_or_404(maquina_id) # Verifica se a máquina existe
        query = Manutencao.query.filter_by(maquina_id=maquina_id)

        # Adicionar filtros de período, tipo, etc., se necessário, como em get_manutencoes

        manutencoes = query.order_by(Manutencao.data_entrada.desc()).all()
        output = []
        for manutencao in manutencoes:
            manutencao_data = {
                "id": manutencao.id,
                "horimetro_hodometro": manutencao.horimetro_hodometro,
                "data_entrada": manutencao.data_entrada.isoformat(),
                "data_saida": manutencao.data_saida.isoformat() if manutencao.data_saida else None,
                "tipo_manutencao": manutencao.tipo_manutencao.value,
                "categoria_servico": manutencao.categoria_servico.value,
                "categoria_outros_especificacao": manutencao.categoria_outros_especificacao,
                "comentario": manutencao.comentario,
                "responsavel_servico": manutencao.responsavel_servico,
                "custo": manutencao.custo
            }
            output.append(manutencao_data)
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar histórico de manutenções: {e}"}), 500

