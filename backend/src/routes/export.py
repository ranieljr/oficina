from flask import Blueprint, Response, request, jsonify, send_file, current_app
from io import BytesIO
from datetime import datetime
import pandas as pd
import xlsxwriter
from functools import wraps
from src.models.models import Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum

# Cria Blueprint com prefixo '/export'
export_bp = Blueprint("export_bp", __name__, url_prefix="/export")

# Decorator para verificar roles
def role_required(roles):
    if not isinstance(roles, list):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_app.logger.debug(f"Verificando roles: {roles} para {request.path}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Função de filtro (implemente sua lógica real)
def _get_filtered_manutencoes(args):
    # Exemplo: retornar lista de Manutencao baseada em args
    # return Manutencao.query.filter(...).all()
    ...

@export_bp.route("/manutencoes/excel", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():
    try:
        manutencoes = _get_filtered_manutencoes(request.args)
        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

        # Monta DataFrame
        df = pd.DataFrame([{
            "ID": m.id,
            "Máquina": m.maquina.nome,
            "Frota": m.maquina.numero_frota,
            "Entrada": m.data_entrada.strftime("%d/%m/%Y %H:%M") if m.data_entrada else "",
            "Saída": m.data_saida.strftime("%d/%m/%Y %H:%M") if m.data_saida else "",
            "Horímetro": m.horimetro_hodometro,
            "Tipo": m.tipo_manutencao.value,
            "Categoria": m.categoria_servico.value,
            "Específico": (m.categoria_outros_especificacao if m.categoria_servico == CategoriaServicoEnum.OUTROS else ""),
            "Comentário": m.comentario or "",
            "Responsável": m.responsavel_servico or "",
            "Custo (R$)": m.custo or 0
        } for m in manutencoes])

        # Gera Excel em memória
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter", options={'strings_to_urls': False}) as writer:
            df.to_excel(writer, index=False, sheet_name="Manutenções")
        buf.seek(0)

        # Debug: log tamanho e magic bytes
        first_bytes = buf.read(4)
        size = buf.getbuffer().nbytes
        current_app.logger.info(f"Excel gerado: {size} bytes; magic={first_bytes!r}")
        buf.seek(0)

        # Envia com send_file e flags anti-cache
        filename = f"manutencoes_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        return send_file(
            buf,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            conditional=False,
            cache_timeout=0,
            add_etags=False
        )

    except Exception as e:
        current_app.logger.exception("Erro interno ao gerar Excel")
        return jsonify({"message": f"Erro interno (Excel): {e}"}), 500

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
