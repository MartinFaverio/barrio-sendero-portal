from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from datetime import datetime
from models.rubro import Rubro  # ← Importa el modelo Rubro correctamente
from models.opiniones import OpinionProveedor

proveedores_bp = Blueprint('proveedores', __name__)

class Proveedor(db.Model):
    __tablename__ = 'proveedores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Relación con Rubro
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubro.id'), nullable=False)
    rubro = db.relationship('Rubro', backref='proveedores')
    opiniones = db.relationship('OpinionProveedor', back_populates='proveedor')

    descripcion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    direccion = db.Column(db.String(200))
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    emergencia = db.Column(db.Boolean, default=False)
    atencion_24hs = db.Column(db.Boolean, default=False)
    foto_nombre = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)    

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    @property
    def promedio(self):
        votos = self.opiniones
        if not votos:
            return 0
        return sum(
            (v.atencion + v.puntualidad + v.variedad + v.confiabilidad) / 4
            for v in votos
        ) / len(votos)