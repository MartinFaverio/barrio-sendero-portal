from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db

class Confirmacion(db.Model):
    __tablename__ = 'confirmaciones'

    id = Column(Integer, primary_key=True)
    visitante_id = Column(Integer, ForeignKey('visitantes.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.now)
    confirmado = Column(Boolean, default=False)

    visitante = relationship("Visitante", backref="confirmacion")