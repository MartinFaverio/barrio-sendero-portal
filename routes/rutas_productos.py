from flask import Blueprint, request, redirect, url_for, flash, session, current_app, render_template
from models.producto import Producto
from models.proveedor import Proveedor
from models.opiniones import OpinionProducto
from extensions import db
from werkzeug.utils import secure_filename
from utils.utils_imagenes import allowed_file, is_valid_mime, validate_image, convert_to_webp
import os

productos_bp = Blueprint('productos_bp', __name__)

@productos_bp.route('/subir_producto', methods=['POST'])
def subir_producto():
    if 'proveedor_id' not in session:
        return redirect(url_for('sesion_bp.login_proveedor'))

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    foto = request.files['foto']

    if not foto or foto.filename == '':
        flash('No se seleccionó ninguna imagen.')
        return redirect(url_for('proveedores_bp.mi_pagina'))

    if not allowed_file(foto.filename) or not is_valid_mime(foto.stream):
        flash('Formato de imagen no permitido.')
        return redirect(url_for('proveedores_bp.mi_pagina'))

    upload_folder = current_app.config['UPLOAD_FOLDER_PRODUCTOS']

    # ✅ Convertir solo después de validar
    filename = convert_to_webp(foto, upload_folder)
    file_path = os.path.join(upload_folder, filename)

    es_valida, mensaje = validate_image(file_path)
    if not es_valida:
        os.remove(file_path)
        flash(mensaje)
        return redirect(url_for('proveedores_bp.mi_pagina'))

    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        foto_nombre=filename,
        proveedor_id=session['proveedor_id']
    )
    db.session.add(nuevo_producto)
    db.session.commit()

    flash('Producto subido correctamente.')
    return redirect(url_for('proveedores_bp.mi_pagina'))



@productos_bp.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if 'proveedor_id' not in session:
        return redirect(url_for('sesion_bp.login_proveedor'))

    producto = Producto.obtener_producto_por_id(id)
    if producto.proveedor_id != session['proveedor_id']:
        return "Acceso no autorizado", 403

    if producto.foto_nombre:
        ruta_imagen = os.path.abspath(os.path.join('static', 'img_productos', producto.foto_nombre))
        if os.path.exists(ruta_imagen):
            try:
                os.remove(ruta_imagen)
            except Exception as e:
                print(f"No se pudo eliminar la imagen: {e}")

    Producto.eliminar_producto_por_id(id)
    return redirect(url_for('proveedores_bp.mi_pagina'))


@productos_bp.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'proveedor_id' not in session:
        return redirect(url_for('sesion_bp.login_proveedor'))

    producto = Producto.obtener_producto_por_id(id)
    if producto.proveedor_id != session['proveedor_id']:
        return "Acceso no autorizado", 403

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']

        foto = request.files.get('foto')
        if foto and foto.filename != '':
            from utils.utils_imagenes import convert_to_webp
            upload_folder = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
            nombre_archivo = convert_to_webp(foto, upload_folder)

            # Eliminar imagen anterior si existe
            if producto.foto_nombre:
                ruta_anterior = os.path.abspath(os.path.join(upload_folder, producto.foto_nombre))
                if os.path.exists(ruta_anterior):
                    try:
                        os.remove(ruta_anterior)
                    except Exception as e:
                        print(f"No se pudo eliminar la imagen anterior: {e}")

            producto.foto_nombre = nombre_archivo

        db.session.commit()
        flash('Producto editado correctamente.')
        return redirect(url_for('proveedores_bp.mi_pagina'))

    return render_template('editar_producto.html', producto=producto, origen='proveedor')


@productos_bp.route('/ver_producto/<int:id>')
def ver_producto(id):
    producto = Producto.query.get_or_404(id)
    opiniones = OpinionProducto.query.filter_by(producto_id=id).order_by(OpinionProducto.fecha.desc()).all()
    return render_template('ver_producto.html', producto=producto, opiniones=opiniones)


@productos_bp.route('/admin/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto_admin(id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    producto = Producto.query.get_or_404(id)
    proveedores = Proveedor.query.all()

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.proveedor_id = request.form['proveedor_id']

        imagen = request.files.get('foto')
        if imagen and imagen.filename != '':
            from utils.utils_imagenes import convert_to_webp
            upload_folder = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
            nombre_archivo = convert_to_webp(imagen, upload_folder)

            # Eliminar imagen anterior si existe
            if producto.foto_nombre:
                ruta_anterior = os.path.abspath(os.path.join(upload_folder, producto.foto_nombre))
                if os.path.exists(ruta_anterior):
                    try:
                        os.remove(ruta_anterior)
                    except Exception as e:
                        print(f"No se pudo eliminar la imagen anterior: {e}")

            producto.foto_nombre = nombre_archivo

        db.session.commit()
        flash('Producto editado correctamente.')
        return redirect(url_for('admin_bp.panel_admin'))

    return render_template('editar_producto.html', producto=producto, proveedores=proveedores, origen='admin')


@productos_bp.route('/admin/eliminar_producto/<int:id>')
def eliminar_producto_admin(id):
    if not session.get('es_admin'):
        return redirect(url_for('sesion_bp.login'))

    producto = Producto.query.get_or_404(id)

    if producto.foto_nombre:
        ruta_imagen = os.path.join('static/img_productos', producto.foto_nombre)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('admin_bp.panel_admin'))