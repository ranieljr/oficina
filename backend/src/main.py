import os
import sys
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.config import Config
from src.models.models import db  # instância única de SQLAlchemy
from src.routes.auth import auth_bp
from src.routes.maquinas import maquinas_bp
from src.routes.manutencoes import manutencoes_bp
from src.routes.export import export_bp

# Garante PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

# Logging
logging.basicConfig(level=logging.INFO)

# Cria app
app = Flask(
    __name__, 
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    static_url_path=""
)

CORS(app, resources={
    r'/api/*': {"origins": "*"}, 
    })

# 1) Carrega Config padrão
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 2) Lê VARS de ambiente e loga
logging.info(f"ENV DATABASE_URL={os.getenv('DATABASE_URL')!r}")
logging.info(f"ENV INTERNAL_DATABASE_URL={os.getenv('INTERNAL_DATABASE_URL')!r}")
logging.info(f"ENV EXTERNAL_DATABASE_URL={os.getenv('EXTERNAL_DATABASE_URL')!r}")

database_url = (
    os.getenv('DATABASE_URL')
    or os.getenv('INTERNAL_DATABASE_URL')
    or os.getenv('EXTERNAL_DATABASE_URL')
)
logging.info(f"▶ database_url resolvida = {database_url!r}")

if not database_url:
    raise RuntimeError(
        "A variável DATABASE_URL não está definida. "
        "Use INTERNAL_DATABASE_URL em produção e EXTERNAL_DATABASE_URL para dev local."
    )

# 3) Ajusta prefixo do Postgres, se necessário
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 4) Inicializa o db importado
db.init_app(app)

# 5) Registra blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(manutencoes_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/export')

# 6) Cria tabelas (apenas se for o seu fluxo)
with app.app_context():
    db.create_all()
    logging.info("Tabelas criadas com sucesso!")

# 7) Rotas únicas para frontend e healthcheck
@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # se for um arquivo estático válido, devolve-o
    full_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(full_path):
        return app.send_static_file(path)
    # senão devolve o index.html
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
@app.after_request
def disable_caching(response):
    response.headers.pop("ETag", None)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    # força status 200 mesmo que o cliente envie If-None-Match/Since
    if response.status_code == 304:
        response.status_code = 200
    return response