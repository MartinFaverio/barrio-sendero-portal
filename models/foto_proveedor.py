from extensions import db

class FotoProveedor(db.Model):
    __tablename__ = 'fotos_proveedor'

    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    comentario = db.Column(db.Text)

    proveedor = db.relationship('Proveedor', backref='fotos')