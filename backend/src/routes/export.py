from flask import Blueprint, request, jsonify, Response
from io import BytesIO
from datetime import datetime
import pandas as pd
import os
import pdfkit
from src.models.models import Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum
from functools import wraps

WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
pdf = pdfkit.from_string("Hello PDF", False, configuration=config)

export_bp = Blueprint("export_bp", __name__)

def role_required(roles):
    if not isinstance(roles, list):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Verificando roles: {roles}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def _get_filtered_manutencoes(args):
    query = Manutencao.query.join(Maquina)
    maquina_id = args.get("maquina_id")
    if maquina_id and maquina_id.lower() != 'todas':
        query = query.filter(Manutencao.maquina_id == int(maquina_id))
    tipo = args.get("tipo_manutencao")
    if tipo and tipo.lower() != 'todos':
        query = query.filter(Manutencao.tipo_manutencao == TipoManutencaoEnum(tipo))
    start_date = args.get("start_date")
    if start_date:
        dt_inicio = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Manutencao.data_entrada >= dt_inicio)
    end_date = args.get("end_date")
    if end_date:
        dt_fim = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(Manutencao.data_entrada < dt_fim + pd.Timedelta(days=1))
    return query.order_by(Manutencao.data_entrada.desc()).all()

@export_bp.route("/manutencoes/excel", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():
    try:
        manutencoes = _get_filtered_manutencoes(request.args)
        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

        # monta DataFrame...
        df = pd.DataFrame([
        {
            "ID": m.id,
            "Máquina": m.maquina.nome,
            "Frota": m.maquina.numero_frota,
            "Entrada": m.data_entrada.strftime("%d/%m/%Y %H:%M") if m.data_entrada else "",
            "Saída": m.data_saida.strftime("%d/%m/%Y %H:%M") if m.data_saida else "",
            "Horímetro/Hodômetro": m.horimetro_hodometro,
            "Tipo": m.tipo_manutencao.value,
            "Categoria de Serviço": m.categoria_servico.value,
            "Específico (se outros)": m.categoria_outros_especificacao if m.categoria_servico == CategoriaServicoEnum.OUTROS else None,
            "Comentário": m.comentario,
            "Responsável": m.responsavel_servico,
            "Custo (R$)": m.custo
        }
        for m in manutencoes
        ])
        # escreve em memória
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Manutenções")
        buf.seek(0)
        data = buf.getvalue()

        print("DEBUG XLSX bytes:", data[:4])  # deve ser b'PK\x03\x04'

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        headers = {
            "Content-Type":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": f"attachment; filename=export_manutencoes_{ts}.xlsx",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return Response(data, headers=headers)

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"message": f"Erro interno (Excel): {e}"}), 500

@export_bp.route("/manutencoes/pdf", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_pdf():
    manutencoes = _get_filtered_manutencoes(request.args)
    if not manutencoes:
        return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

    # Monta HTML
    html = "<html><head><meta charset='utf-8'><style>table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ddd;padding:8px;}</style></head><body>"
    html += "<h2>Relatório de Manutenções</h2><table><thead><tr>"
    html += "<th>Máquina</th><th>Frota</th><th>Entrada</th><th>Saída</th><th>Tipo</th><th>Categoria</th><th>Responsável</th><th>Custo</th>"
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

    # Gera PDF bytes
    pdf_bytes = pdfkit.from_string(html, False, configuration=PDFKIT_CONFIG)

    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=relatorio_manutencoes.pdf",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return Response(pdf_bytes, headers=headers)
