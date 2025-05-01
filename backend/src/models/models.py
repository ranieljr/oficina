# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum

db = SQLAlchemy()

class TipoMaquinaEnum(enum.Enum):
    MAQUINA = "máquina"
    IMPLEMENTO = "implemento"
    VEICULO = "veículo"

class TipoControleEnum(enum.Enum):
    HODOMETRO = "hodômetro"
    HORIMETRO = "horímetro"

class StatusMaquinaEnum(enum.Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"

class TipoManutencaoEnum(enum.Enum):
    PREVENTIVA = "preventiva"
    CORRETIVA = "corretiva"

class CategoriaServicoEnum(enum.Enum):
    AUTO_ELETRICA = "Auto elétrica"
    FILTROS_LUBRIFICANTES = "Filtros e lubrificantes"
    PNEUS_BORRACHAS = "Pneus e borrachas"
    REFORMA = "Reforma"
    RETIFICA_MOTORES = "Retífica de motores"
    AR_CONDICIONADO = "Ar-condicionado"
    MATERIAL_RODANTE = "Material rodante"
    OUTROS = "Outros"

class RoleEnum(enum.Enum):
    GESTOR = "gestor"
    MECANICO = "mecanico"
    ADMINISTRADOR = "administrador"

class Maquina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(Enum(TipoMaquinaEnum), nullable=False)
    numero_frota = db.Column(db.String(50), unique=True, nullable=False)
    data_aquisicao = db.Column(db.Date, nullable=False)
    tipo_controle = db.Column(Enum(TipoControleEnum), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    status = db.Column(Enum(StatusMaquinaEnum), default=StatusMaquinaEnum.ATIVO, nullable=False)
    manutencoes = db.relationship('Manutencao', backref='maquina', lazy=True)

class Manutencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    horimetro_hodometro = db.Column(db.Float, nullable=False)
    data_entrada = db.Column(db.DateTime, nullable=False)
    data_saida = db.Column(db.DateTime)
    tipo_manutencao = db.Column(Enum(TipoManutencaoEnum), nullable=False)
    categoria_servico = db.Column(Enum(CategoriaServicoEnum), nullable=False)
    categoria_outros_especificacao = db.Column(db.String(255)) # Para quando a categoria for "Outros"
    comentario = db.Column(db.Text)
    responsavel_servico = db.Column(db.String(100), nullable=False)
    custo = db.Column(db.Float) # Campo simples para custo

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Armazenar hash da senha
    role = db.Column(Enum(RoleEnum), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.username}>'

