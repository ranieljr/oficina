from flask import Blueprint, request, jsonify, send_file, current_app
from io import BytesIO
from datetime import datetime
import pandas as pd
from functools import wraps
from src.models.models import Maquina, Manutencao, TipoManutencaoEnum, CategoriaServicoEnum

export_bp = Blueprint("export_bp", __name__)

def role_required(roles):
    if not isinstance(roles, list):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Aqui você colocaria a lógica real de verificação de token/usuário,
            # por enquanto só vamos imprimir e seguir em frente:
            current_app.logger.debug(f"Verificando roles: {roles} para o usuário em {request.path}")
            return f(*args, **kwargs)
        return decorated_function

    return decorator
    # seu decorator aqui (igual ao atual)
    ...

def _get_filtered_manutencoes(args):
    # seus filtros aqui (igual ao atual)
    ...

@export_bp.route("/export/manutencoes/excel", methods=["GET"])
@role_required(["gestor", "administrador"])
def export_manutencoes_excel():
    try:
        manutencoes = _get_filtered_manutencoes(request.args)
        if not manutencoes:
            return jsonify({"message": "Nenhuma manutenção encontrada."}), 404

        # monta o DataFrame
        df = pd.DataFrame([{
            "ID":             m.id,
            "Máquina":        m.maquina.nome,
            "Frota":          m.maquina.numero_frota,
            "Entrada":        m.data_entrada.strftime("%d/%m/%Y %H:%M") if m.data_entrada else "",
            "Saída":          m.data_saida.strftime("%d/%m/%Y %H:%M")   if m.data_saida   else "",
            "Horímetro":      m.horimetro_hodometro,
            "Tipo":           m.tipo_manutencao.value,
            "Categoria":      m.categoria_servico.value,
            "Específico":     (m.categoria_outros_especificacao
                                 if m.categoria_servico == CategoriaServicoEnum.OUTROS
                                 else ""),
            "Comentário":     m.comentario  or "",
            "Responsável":    m.responsavel_servico or "",
            "Custo (R$)":     m.custo or 0
        } for m in manutencoes])

        # escreve em memória usando openpyxl
        buf = BytesIO()
        writer = pd.ExcelWriter(buf, engine="xlsxwriter", 
                                options={'strings_to_urls': False})
        df.to_excel(writer, index=False, sheet_name="Manutenções")
        # garante gravação e liberação de recursos
        writer.close()
    
        # reposiciona ponteiro antes de enviar
        buf.seek(0)

        # 1) Teste ler o que você acabou de gerar:
        buf.seek(0)
        try:
            df_teste = pd.read_excel(buf)
            current_app.logger.debug(f"Preview gerado sem erro, {len(df_teste)} linhas lidas")
        except Exception as e:
            current_app.logger.error(f"Buffer inválido: não é um .xlsx válido — {e}")

        # 2) Confira os 4 primeiros bytes (deveriam ser 'PK\\x03\\x04'):
        buf.seek(0)
        magic = buf.read(4)
        current_app.logger.debug(f"Magic bytes do Excel: {magic!r}")
        buf.seek(0)

        filename = f"export_manutencoes_{datetime.now():%Y%m%d_%H%M%S}.xlsx"

        data = buf.getvalue()
        headers = {
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(data)),
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return send_file(
            buf,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            conditional=False,        # força sempre reenvio do corpo
            cache_timeout=0           # inibe cache intermediários
        )
        
    except Exception as e:      
        # imprime o traceback completo no console do Flask
        import traceback; traceback.print_exc()
        # e retorna o JSON pro front
        return jsonify({"message": f"Erro interno (Excel): {e}"}), 500

@export_bp.route("/export/manutencoes/pdf", methods=["GET"])
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
