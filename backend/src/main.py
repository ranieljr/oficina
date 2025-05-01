import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.models import db, Maquina, Manutencao, Usuario
from src.routes.auth import auth_bp
from src.routes.maquinas import maquinas_bp
from src.routes.manutencoes import manutencoes_bp
from src.routes.export import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Temporariamente permitir todas as origens para teste
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(manutencoes_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'RANjun02!')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    return f"Serving: {path}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
