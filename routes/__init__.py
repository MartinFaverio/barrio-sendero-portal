from .rutas_proveedores import proveedores_bp
from .rutas_productos import productos_bp
from .rutas_admin import admin_bp
from .rutas_publicas import publicas_bp
from .rutas_sesion import sesion_bp
from .rutas_visitante import visitante_bp
from .rutas_opiniones import opiniones_bp
from .rutas_mapa import bp_mapa
from .rutas_imagenes import imagenes_bp

def register_routes(app):
    app.register_blueprint(proveedores_bp, url_prefix='/proveedores', name='proveedores_bp')
    app.register_blueprint(productos_bp, url_prefix='/productos', name='productos_bp')
    app.register_blueprint(admin_bp, url_prefix='/admin', name='admin_bp')
    app.register_blueprint(publicas_bp, url_prefix='', name='publicas_bp')  # raíz del sitio
    app.register_blueprint(sesion_bp, url_prefix='/sesion', name='sesion_bp')
    app.register_blueprint(visitante_bp, url_prefix='/visitante', name='visitante_bp')
    app.register_blueprint(opiniones_bp, url_prefix='/opiniones', name='opiniones_bp')
    app.register_blueprint(bp_mapa, url_prefix='/mapa', name='bp_mapa')
    app.register_blueprint(imagenes_bp, url_prefix='/imagenes', name='imagenes_bp')