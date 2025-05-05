from flask import Blueprint, Response, request, jsonify, send_file, current_app
from io import BytesIO
from datetime import datetime
import xlsxwriter
from functools import wraps
from src.models.models import Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum

# Blueprint configurado em '/export'
export_bp = Blueprint("export_bp", __name__)

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
    ...

@export_bp.route("/manutencoes/excel", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():
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
        headers = ['ID','Máquina','Frota','Entrada','Saída','Horímetro','Tipo','Categoria','Específico','Comentário','Responsável','Custo (R$)']
        for col, h in enumerate(headers):
            ws.write(0, col, h)

        # Linhas
        for row_idx, m in enumerate(manutencoes, start=1):
            values = [
                m.id,
                m.maquina.nome,
                m.maquina.numero_frota,
                m.data_entrada.strftime('%d/%m/%Y %H:%M') if m.data_entrada else '',
                m.data_saida.strftime('%d/%m/%Y %H:%M') if m.data_saida else '',
                m.horimetro_hodometro,
                m.tipo_manutencao.value,
                m.categoria_servico.value,
                m.categoria_outros_especificacao if m.categoria_servico==CategoriaServicoEnum.OUTROS else '',
                m.comentario or '',
                m.responsavel_servico or '',
                m.custo or 0
            ]
            for col, val in enumerate(values):
                ws.write(row_idx, col, val)

        workbook.close()
        # Ajusta buffer
        buf.seek(0)

        # Debug: tamanho e magic
        data = buf.getvalue()
        size = len(data)
        magic = data[:4]
        current_app.logger.info(f"DEBUG Excel -> bytes: {size}; magic: {magic!r}")

        # Envio
        filename = f"manutencoes_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        return send_file(
            BytesIO(data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            conditional=False,
            cache_timeout=0,
            add_etags=False
        )

    except Exception as e:
        current_app.logger.exception('Falha ao gerar Excel')
        return jsonify({'message': f'Erro interno (Excel): {e}'}), 500

@export_bp.route("/manutencoes/pdf", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_pdf():
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

    pdf_bytes = pdfkit.from_string(html, False, configuration=PDFKIT_CONFIG)
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=relatorio_manutencoes.pdf",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return Response(pdf_bytes, headers=headers)
