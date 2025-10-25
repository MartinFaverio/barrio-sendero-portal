from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db

class OpinionProducto(db.Model):
    __tablename__ = 'opiniones_producto'

    id = Column(Integer, primary_key=True)
    visitante_id = Column(Integer, ForeignKey('visitantes.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('producto.id'), nullable=False)
    comentario = Column(Text)
    fecha = Column(DateTime, default=datetime.now)

    # Sistema de estrellas (1 a 5)
    calidad = Column(Integer)        # diseño, funcionalidad
    precio = Column(Integer)         # relación costo-beneficio
    utilidad = Column(Integer)       # cumple su propósito
    presentacion = Column(Integer)   # estética, empaque

    visitante = relationship("Visitante", back_populates="opiniones_producto")
    producto = relationship("Producto", back_populates="opiniones")

class OpinionProveedor(db.Model):
    __tablename__ = 'opiniones_proveedor'

    id = Column(Integer, primary_key=True)
    visitante_id = Column(Integer, ForeignKey('visitantes.id'), nullable=False)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), nullable=False)
    comentario = Column(Text)
    fecha = Column(DateTime, default=datetime.now)

    # Sistema de estrellas (1 a 5)
    atencion = Column(Integer)       # trato humano
    puntualidad = Column(Integer)    # cumplimiento de tiempos
    variedad = Column(Integer)       # opciones ofrecidas
    confiabilidad = Column(Integer)  # confianza y transparencia

    visitante = relationship("Visitante", back_populates="opiniones_proveedor")
    proveedor = relationship("Proveedor", back_populates="opiniones")