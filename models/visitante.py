from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db

class Visitante(db.Model):
    __tablename__ = 'visitantes'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    contraseña_hash = Column(String(255), nullable=False)
    confirmado = db.Column(db.Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.now)

    opiniones_producto = relationship("OpinionProducto", back_populates="visitante")

    opiniones_proveedor = relationship("OpinionProveedor", back_populates="visitante")
