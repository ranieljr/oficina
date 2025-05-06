import os
import sys
import logging
from flask import Flask, request, make_response, send_from_directory
from src.config import Config
from src.models.models import db
from src.routes.auth import auth_bp
from src.routes.maquinas import maquinas_bp
from src.routes.manutencoes import manutencoes_bp
from src.routes.export import export_bp

# PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO)

ALLOWED_ORIGINS = {
    "https://laufoficina.vercel.app",
    "https://laufoficina-ranieljrs-projects.vercel.app"
}

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    static_url_path=""
)

# Carrega Config
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Banco
database_url = (
    os.getenv('DATABASE_URL')
    or os.getenv('INTERNAL_DATABASE_URL')
    or os.getenv('EXTERNAL_DATABASE_URL')
)
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(manutencoes_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/export')

# Cria tabelas (dev)
with app.app_context():
    db.create_all()
    logging.info("Tabelas criadas com sucesso!")

# Healthcheck e front-end
@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    full = os.path.join(app.static_folder, path)
    if path and os.path.exists(full):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# 1) Lida com preflight CORS para qualquer rota /api/*
@app.route('/api/<path:any>', methods=['OPTIONS'])
def preflight(any):
    origin = request.headers.get('Origin', '')
    resp = make_response()
    resp.status_code = 204
    if origin in ALLOWED_ORIGINS:
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return resp

# 2) Adiciona header CORS em todas as respostas de /api/*
@app.after_request
def add_cors(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS and request.path.startswith('/api/'):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    # mantém seu disable_caching se quiser
    response.headers.pop("ETag", None)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    if response.status_code == 304:
        response.status_code = 200
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
