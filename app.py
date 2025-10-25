import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from config import Config
from extensions import db
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='data.env')

# Inicializar la app Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configuración de imágenes
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB
app.config['UPLOAD_FOLDER'] = 'static/img_proveedores'
app.config['UPLOAD_FOLDER_PRODUCTOS'] = 'static/img_productos'

# Inicializar la base de datos
db.init_app(app)

# Importar modelos
from models.proveedor import Proveedor
from models.visitante import Visitante
from models.producto import Producto
from models.rubro import Rubro
from models.confirmaciones import Confirmacion
from models.opiniones import OpinionProducto, OpinionProveedor

# Crear tablas y cargar rubros iniciales solo en producción (Render)
if os.getenv("RENDER") == "true":
    with app.app_context():
        db.create_all()

        rubros_iniciales = [
            'Carniceria', 'Panaderia', 'Gastronomia', 'Ferreteria', 'Verduleria',
            'Desayunos', 'Electricidad', 'Escolar', 'Farmacia', 'Libreria',
            'Masajes', 'Otros', 'Peluqueria', 'Perfumeria', 'Salud',
            'Transporte', 'Veterinaria'
        ]
        for nombre in rubros_iniciales:
            if not Rubro.query.filter_by(nombre=nombre).first():
                db.session.add(Rubro(nombre=nombre))
        db.session.commit()
        print("✅ Rubros iniciales consagrados correctamente.")

# Registrar rutas consagradas
from routes import register_routes
register_routes(app)

print("Blueprints consagrados correctamente")

# Ejecutar la app
if __name__ == '__main__':

    app.run(debug=True)

