from flask_sqlalchemy import SQLAlchemy
from extensions import db
import os
from models.proveedor import Proveedor
from models.opiniones import OpinionProducto



class Producto(db.Model):
    __tablename__ = 'producto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    foto_nombre = db.Column(db.String(255))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))

    proveedor = db.relationship('Proveedor', backref='productos')
    opiniones = db.relationship('OpinionProducto', back_populates='producto')

    @staticmethod
    def obtener_producto_por_id(id):
        return Producto.query.get(id)

    @staticmethod
    def actualizar_producto(id, nombre, descripcion):
        producto = Producto.query.get(id)
        if producto:
            producto.nombre = nombre
            producto.descripcion = descripcion
            db.session.commit()

    @staticmethod
    def eliminar_producto_por_id(id):
        producto = Producto.query.get(id)
        if producto and producto.foto_nombre:
            ruta_imagen = os.path.abspath(os.path.join('static', 'img_productos', producto.foto_nombre))
            if os.path.exists(ruta_imagen):
                try:
                    os.remove(ruta_imagen)
                    print(f"Imagen eliminada: {ruta_imagen}")
                except Exception as e:
                    print(f"No se pudo eliminar la imagen: {e}")
        db.session.delete(producto)
        db.session.commit()

    @property
    def promedio(self):
        votos = self.opiniones
        if not votos:
            return 0
        return sum(
            (v.calidad + v.precio + v.utilidad + v.presentacion) / 4
            for v in votos
        ) / len(votos)