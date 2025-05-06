from flask import Blueprint, Response, request, jsonify, send_file, current_app, make_response
from io import BytesIO
from datetime import datetime
import xlsxwriter
from functools import wraps
from src.models.models import Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum

# Blueprint configurado em '/export'
export_bp = Blueprint("export_bp", __name__)

@export_bp.after_request
def add_cors_headers(response):
    # Aplica CORS em todas as respostas do blueprint
    response.headers["Access-Control-Allow-Origin"] = "https://laufoficina.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

# Decorator de roles
def role_required(roles):
    if not isinstance(roles, list):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_app.logger.debug(f"Verificando roles {roles} para {request.path}")
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Função de filtros (implemente conforme sua lógica)
def _get_filtered_manutencoes(args):
    return Manutencao.query.all()
    # Exemplo:
    # return Manutencao.query.filter_by(...).all()

@export_bp.route("/manutencoes/excel", methods=["OPTIONS", "GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():
    # Preflight CORS
    if request.method == "OPTIONS":
        return make_response(('', 204))

    try:
        # Busca dados
        manutencoes = _get_filtered_manutencoes(request.args)
        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

        # Cria Excel puro com xlsxwriter
        buf = BytesIO()
        workbook = xlsxwriter.Workbook(buf, {'in_memory': True})
        ws = workbook.add_worksheet('Manutenções')

        # Cabeçalho
        headers = ['ID','Máquina','Frota','Entrada','Saída','Horímetro',
                   'Tipo','Categoria','Específico','Comentário','Responsável','Custo (R$)']
        for col, h in enumerate(headers):
            ws.write(0, col, h)

        # Linhas
        for row_idx, m in enumerate(manutencoes, start=1):
            values = [
                m.id,
                m.maquina.nome if m.maquina else '',
                m.maquina.numero_frota if m.maquina else '',
                m.data_entrada.strftime('%d/%m/%Y %H:%M') if m.data_entrada else '',
                m.data_saida.strftime('%d/%m/%Y %H:%M') if m.data_saida else '',
                m.horimetro_hodometro or '',
                m.tipo_manutencao.value if m.tipo_manutencao else '',
                m.categoria_servico.value if m.categoria_servico else '',
                m.categoria_outros_especificacao if getattr(m, 'categoria_servico', None) == CategoriaServicoEnum.OUTROS else '',
                m.comentario or '',
                m.responsavel_servico or '',
                m.custo or 0
            ]
            for col, val in enumerate(values):
                ws.write(row_idx, col, val)

        workbook.close()
        buf.seek(0)
        data = buf.getvalue()

        current_app.logger.info(f"Excel gerado com {len(data)} bytes")
        filename = f"manutencoes.xlsx"

        headers = {
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }

        return Response(data, headers=headers)

    except Exception as e:
        current_app.logger.exception('Falha ao gerar Excel')
        return jsonify({'message': f'Erro interno (Excel): {e}'}), 500

@export_bp.route("/manutencoes/pdf", methods=["OPTIONS", "GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_pdf():
    # Preflight CORS
    if request.method == "OPTIONS":
        return make_response(('', 204))

    manutencoes = _get_filtered_manutencoes(request.args)
    if not manutencoes:
        return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

    html = "<html><head><meta charset='utf-8'><style>table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ddd;padding:8px;}</style></head><body>"
    html += "<h2>Relatório de Manutenções</h2><table><thead><tr>"
    cols = ["Máquina","Frota","Entrada","Saída","Tipo","Categoria","Responsável","Custo"]
    for c in cols:
        html += f"<th>{c}</th>"
    html += "</tr></thead><tbody>"
    for m in manutencoes:
        html += (
            f"<tr><td>{m.maquina.nome}</td>"
            f"<td>{m.maquina.numero_frota}</td>"
            f"<td>{m.data_entrada.strftime('%d/%m/%Y')}</td>"
            f"<td>{m.data_saida.strftime('%d/%m/%Y') if m.data_saida else '-'}</td>"
            f"<td>{m.tipo_manutencao.value}</td>"
            f"<td>{m.categoria_servico.value}</td>"
            f"<td>{m.responsavel_servico}</td>"
            f"<td>{m.custo or '-'}</td></tr>"
        )
    html += "</tbody></table></body></html>"

    from flask import current_app
    # Garante configuração PDFKIT_CONFIG disponível
    pdf_bytes = current_app.config.get('PDFKIT_CONFIG') and pdfkit.from_string(html, False, configuration=current_app.config['PDFKIT_CONFIG']) or pdfkit.from_string(html, False)
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=relatorio_manutencoes.pdf",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return Response(pdf_bytes, headers=headers)
