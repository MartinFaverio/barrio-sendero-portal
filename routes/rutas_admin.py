from flask import Blueprint, render_template, redirect, session, request, url_for, current_app, flash
from models.opiniones import OpinionProducto, OpinionProveedor
from models.producto import Producto
from models.proveedor import Proveedor
from models.visitante import Visitante
from models.rubro import Rubro
from extensions import db
from werkzeug.utils import secure_filename
from utils.utils_imagenes import allowed_file, is_valid_mime, validate_image, convert_to_webp, procesar_imagen_proveedor
import os

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/opiniones')
def ver_opiniones():
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    visitante = request.args.get('visitante')
    producto_nombre = request.args.get('producto')
    proveedor_nombre = request.args.get('proveedor')
    fecha = request.args.get('fecha')

    opiniones_producto = OpinionProducto.query
    opiniones_proveedor = OpinionProveedor.query

    # Filtro por visitante
    if visitante:
        opiniones_producto = opiniones_producto.join(Visitante).filter(Visitante.nombre.ilike(f"%{visitante}%"))
        opiniones_proveedor = opiniones_proveedor.join(Visitante).filter(Visitante.nombre.ilike(f"%{visitante}%"))

    # Filtro por producto
    if producto_nombre:
        opiniones_producto = opiniones_producto.join(Producto).filter(Producto.nombre == producto_nombre)
        # Mostrar solo opiniones del proveedor de ese producto
        producto_obj = Producto.query.filter_by(nombre=producto_nombre).first()
        if producto_obj:
            opiniones_proveedor = opiniones_proveedor.join(Proveedor).filter(Proveedor.id == producto_obj.proveedor_id)
        else:
            opiniones_proveedor = opiniones_proveedor.filter(False)  # No mostrar nada si no se encuentra

    # Filtro por proveedor
    if proveedor_nombre:
        opiniones_proveedor = opiniones_proveedor.join(Proveedor).filter(Proveedor.nombre == proveedor_nombre)
        # Mostrar solo opiniones de productos de ese proveedor
        opiniones_producto = opiniones_producto.join(Producto).join(Proveedor).filter(Proveedor.nombre == proveedor_nombre)

    # Filtro por fecha
    if fecha:
        opiniones_producto = opiniones_producto.filter(OpinionProducto.fecha == fecha)
        opiniones_proveedor = opiniones_proveedor.filter(OpinionProveedor.fecha == fecha)

    opiniones_producto = opiniones_producto.all()
    opiniones_proveedor = opiniones_proveedor.all()

    conceptos_producto = ['calidad', 'precio', 'utilidad', 'presentacion']
    conceptos_proveedor = ['atencion', 'puntualidad', 'variedad', 'confiabilidad']

    def obtener_valores(opiniones, conceptos):
        return {
            op.id: {c: getattr(op, c, 0) for c in conceptos}
            for op in opiniones
        }

    valores_producto = obtener_valores(opiniones_producto, conceptos_producto)
    valores_proveedor = obtener_valores(opiniones_proveedor, conceptos_proveedor)

    productos = Producto.query.order_by(Producto.nombre).all()
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()

    return render_template('admin_opiniones.html',
                        opiniones_producto=opiniones_producto,
                        opiniones_proveedor=opiniones_proveedor,
                        valores_producto=valores_producto,
                        valores_proveedor=valores_proveedor,
                        conceptos=conceptos_producto + conceptos_proveedor,
                        productos=productos,
                        proveedores=proveedores)


@admin_bp.route('/editar_opinion/<tipo>/<int:id>', methods=['GET', 'POST'])
def editar_opinion(tipo, id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    if tipo == 'producto':
        op = OpinionProducto.query.get_or_404(id)
        conceptos = ['calidad', 'precio', 'utilidad', 'presentacion']
    else:
        op = OpinionProveedor.query.get_or_404(id)
        conceptos = ['atencion', 'puntualidad', 'variedad', 'confiabilidad']

    if request.method == 'POST':
        op.comentario = request.form.get('comentario')
        for c in conceptos:
            valor = request.form.get(c)
            setattr(op, c, int(valor) if valor else None)
        db.session.commit()
        return redirect(url_for('admin_bp.ver_opiniones'))

    valores = {c: getattr(op, c) for c in conceptos}
    return render_template('admin_editar_opinion.html', op=op, tipo=tipo, conceptos=conceptos, valores=valores)


@admin_bp.route('/eliminar_opinion/<tipo>/<int:id>', methods=['POST'])
def eliminar_opinion(tipo, id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    op = OpinionProducto.query.get(id) if tipo == 'producto' else OpinionProveedor.query.get(id)
    if op:
        db.session.delete(op)
        db.session.commit()

    return redirect(url_for('admin_bp.ver_opiniones'))


@admin_bp.route('/editar_proveedor/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    proveedor = Proveedor.query.get_or_404(id)
    rubros = Rubro.query.all()

    if request.method == 'POST':
        proveedor.nombre = request.form['nombre']
        proveedor.descripcion = request.form['descripcion']
        proveedor.rubro_id = request.form['rubro_id']
        proveedor.emergencia = 'emergencia' in request.form
        proveedor.atencion_24hs = 'atencion_24hs' in request.form

        try:
            proveedor.latitud = float(request.form.get('latitud'))
        except (TypeError, ValueError):
            proveedor.latitud = None

        try:
            proveedor.longitud = float(request.form.get('longitud'))
        except (TypeError, ValueError):
            proveedor.longitud = None

        foto = request.files.get('foto')
        upload_folder = current_app.config['UPLOAD_FOLDER']
        ok, mensaje = procesar_imagen_proveedor(proveedor, foto, upload_folder)

        if not ok and foto and foto.filename != '':
            flash(mensaje, 'danger')
            return redirect(request.url)

        db.session.commit()
        flash('Proveedor editado correctamente.')
        return redirect(url_for('admin_bp.panel_admin'))

    return render_template('editar_proveedor.html', proveedor=proveedor, rubros=rubros)


@admin_bp.route('/eliminar_proveedor/<int:id>')
def eliminar_proveedor(id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    proveedor = Proveedor.query.get_or_404(id)

    if proveedor.foto_nombre:
        ruta_imagen = os.path.join('static/img_proveedores', proveedor.foto_nombre)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    productos = Producto.query.filter_by(proveedor_id=proveedor.id).all()
    for producto in productos:
        db.session.delete(producto)

    db.session.delete(proveedor)
    db.session.commit()
    return redirect(url_for('admin_bp.panel_admin'))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']

        admin_user = os.getenv('ADMIN_USER')
        admin_pass = os.getenv('ADMIN_PASS')

        if usuario == admin_user and clave == admin_pass:
            session.permanent = True  # ✅ Mantener sesión activa
            session['es_admin'] = True
            return redirect(url_for('admin_bp.panel_admin'))
        else:
            flash('Credenciales incorrectas', 'danger')
            return redirect(url_for('admin_bp.login'))

    return render_template('login.html')


@admin_bp.route('/admin')
def panel_admin():
    if not session.get('es_admin'):
        return redirect(url_for('admin_bp.login'))

    proveedores = Proveedor.query.all()
    productos = Producto.query.all()
    return render_template('panel_admin.html',
                        proveedores=proveedores,
                        productos=productos)


@admin_bp.route('/logout')
def logout():
    session.pop('es_admin', None)
    return redirect(url_for('publicas_bp.index'))