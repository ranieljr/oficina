import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Garante que os módulos internos sejam encontrados
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importações do projeto
from src.models.models import db, Maquina, Manutencao, Usuario
from src.routes.auth import auth_bp
from src.routes.maquinas import maquinas_bp
from src.routes.manutencoes import manutencoes_bp
from src.routes.export import export_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Registro de rotas
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(maquinas_bp, url_prefix='/api')
    app.register_blueprint(manutencoes_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')

    return app

app = create_app()
