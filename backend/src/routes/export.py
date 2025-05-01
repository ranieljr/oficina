# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, Response, make_response
from io import BytesIO
#from weasyprint import HTML, CSS
from src.models.models import db, Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum
from datetime import datetime
from functools import wraps
import pandas as pd
import pdfkit
from flask import send_file
# TODO: Importar decorator de autenticação/autorização
# from .auth import login_required, role_required # Exemplo

export_bp = Blueprint("export_bp", __name__)

# Decorator placeholder para simular verificação de role (substituir por real)
def role_required(roles):
    if not isinstance(roles, list): roles = [roles]
    def decorator(f):
        @wraps(f) # Usar se importar wraps de functools
        def decorated_function(*args, **kwargs):
            # Lógica de verificação de role (ex: verificar current_user.role)
            # Por agora, permite tudo para demonstração
            print(f"Verificando roles: {roles}") # Log de simulação
            # Substituir pela lógica real de verificação de roles
            # user_role = getattr(current_user, 'role', None)
            # if not user_role or user_role.value not in roles:
            #     return jsonify({"message": "Acesso não autorizado para esta operação"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _get_filtered_manutencoes(args):
    """Helper function to get filtered maintenance data based on request args."""
    query = Manutencao.query.join(Maquina) # Join para poder ordenar/filtrar por nome da máquina se necessário

    if "maquina_id" in args and args.get("maquina_id") != 'todas':
        query = query.filter(Manutencao.maquina_id == args.get("maquina_id"))
    if "tipo_manutencao" in args and args.get("tipo_manutencao") != 'todos':
        query = query.filter(Manutencao.tipo_manutencao == TipoManutencaoEnum(args.get("tipo_manutencao")))
    if "start_date" in args and args.get("start_date"):
        start_date = datetime.strptime(args.get("start_date"), "%Y-%m-%d")
        query = query.filter(Manutencao.data_entrada >= start_date)
    if "end_date" in args and args.get("end_date"):
        # Adiciona 1 dia para incluir a data final na consulta
        end_date = datetime.strptime(args.get("end_date"), "%Y-%m-%d")
        query = query.filter(Manutencao.data_entrada < end_date + pd.Timedelta(days=1))

    return query.order_by(Manutencao.data_entrada.desc()).all()

# Rota para exportar manutenções para Excel (Gestor, Administrador) - TEMPORARIAMENTE DESABILITADA
@export_bp.route("/export/manutencoes/excel", methods=["GET"])
# @login_required  # pode manter comentado se ainda não implementou login
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():

    try:
        manutencoes = _get_filtered_manutencoes(request.args)

        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada para os filtros selecionados."}), 404

        data_to_export = []
        for man in manutencoes:
            data_to_export.append({
                "ID Manutenção": man.id,
                "Máquina": man.maquina.nome,
                "Nº Frota": man.maquina.numero_frota,
                "Data Entrada": man.data_entrada.strftime("%d/%m/%Y %H:%M") if man.data_entrada else None,
                "Data Saída": man.data_saida.strftime("%d/%m/%Y %H:%M") if man.data_saida else None,
                "Horímetro/Hodômetro": man.horimetro_hodometro,
                "Tipo Manutenção": man.tipo_manutencao.value,
                "Categoria Serviço": man.categoria_servico.value,
                "Outros (Espec.)": man.categoria_outros_especificacao if man.categoria_servico == CategoriaServicoEnum.OUTROS else None,
                "Comentário": man.comentario,
                "Responsável": man.responsavel_servico,
                "Custo (R$)": man.custo
            })

        df = pd.DataFrame(data_to_export)

        # Cria um buffer na memória para o arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Manutencoes')
        output.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_manutencoes_{timestamp}.xlsx"

        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    except ValueError as e: # Captura erro de enum inválido no filtro
        return jsonify({"message": f"Valor de filtro inválido: {e}"}), 400
    except Exception as e:
        print(f"Erro ao exportar para Excel: {e}") # Log do erro
        return jsonify({"message": f"Erro ao exportar manutenções para Excel: {e}"}), 500

# Rota para exportar manutenções para PDF (Gestor, Administrador) - TEMPORARIAMENTE DESABILITADA
@export_bp.route("/export/manutencoes/pdf", methods=["GET"])
# @login_required
@role_required(["gestor", "administrador"])
def export_manutencoes_pdf():
    try:
        manutencoes = _get_filtered_manutencoes(request.args)

        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada para os filtros selecionados."}), 404

        # Gerar HTML para o PDF
        html = "<html><head><meta charset='utf-8'><style>table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px}</style></head><body>"
        html += "<h2>Relatório de Manutenções</h2>"
        html += "<table><thead><tr><th>Máquina</th><th>Frota</th><th>Entrada</th><th>Saída</th><th>Tipo</th><th>Responsável</th><th>Custo</th></tr></thead><tbody>"

        for man in manutencoes:
            html += f"<tr><td>{man.maquina.nome}</td><td>{man.maquina.numero_frota}</td><td>{man.data_entrada.strftime('%d/%m/%Y')}</td><td>{man.data_saida.strftime('%d/%m/%Y') if man.data_saida else '-'}</td><td>{man.tipo_manutencao.value}</td><td>{man.responsavel_servico}</td><td>{man.custo or '-'}</td></tr>"

        html += "</tbody></table></body></html>"

        output_path = "relatorio_manutencoes.pdf"
        pdfkit.from_string(html, output_path)

        return send_file(output_path, mimetype='application/pdf', download_name=output_path)

    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return jsonify({"message": f"Erro ao exportar PDF: {e}"}), 500
# TODO: Adicionar rotas similares para exportar dados de MÁQUINAS (Excel e PDF)
# Ex: /export/maquinas/excel e /export/maquinas/pdf


