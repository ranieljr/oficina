
import os
import sys

# ✅ Garante que a pasta 'backend' esteja no PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS
from src.models.models import db, Maquina, Manutencao, Usuario
from src.routes.auth import auth_bp
from src.routes.maquinas import maquinas_bp
from src.routes.manutencoes import manutencoes_bp
from src.routes.export import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, resources={
    r'/api/*': {"origins": "*"},
    r'/export/*': {"origins": "*"}
})
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:RANjun02!@localhost/laufdb'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.from_object(Config)

# Inicializa com os modelos já importados
db.init_app(app)

# Registra rotas
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(manutencoes_bp, url_prefix="/api")
app.register_blueprint(export_bp, url_prefix='/export')

try:
    with app.app_context():
        db.create_all()
    print("Conexão funcionando e tabelas criadas!")
except Exception as e:
    print("Erro:", e)

@app.route("/", defaults={"path": ""})
def home():
    return "API online com sucesso!"
@app.route("/<path:path>")
def serve(path):
    if path.startswith("api/"):
        return {"message": "Rota não encontrada"}, 404
    return send_from_directory(app.static_folder, "index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response