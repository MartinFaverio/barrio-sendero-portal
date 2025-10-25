from flask import Blueprint, request, redirect, url_for, render_template, flash, session, current_app
from models.proveedor import Proveedor
from models.producto import Producto
from models.rubro import Rubro
from models.opiniones import OpinionProveedor
from extensions import db
from werkzeug.utils import secure_filename
from utils.rubro_iconos import rubro_iconos
from utils.utils_imagenes import allowed_file, is_valid_mime, validate_image, convert_to_webp, procesar_imagen_proveedor
import os

proveedores_bp = Blueprint('proveedores_bp', __name__)

@proveedores_bp.route('/agregar_proveedor', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        rubro_id = request.form['rubro_id']
        descripcion = request.form['descripcion']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        password = request.form['password']
        emergencia = bool(request.form.get('emergencia'))
        atencion_24hs = bool(request.form.get('atencion_24hs'))

        foto = request.files.get('foto')
        foto_nombre = None

        if foto and foto.filename != '' and allowed_file(foto.filename) and is_valid_mime(foto):
            upload_folder = os.path.join('static', 'img_proveedores')
            foto_nombre = convert_to_webp(foto, upload_folder)
            ruta_final = os.path.join(upload_folder, foto_nombre)

            es_valida, mensaje = validate_image(ruta_final)
            if not es_valida:
                os.remove(ruta_final)
                flash(mensaje, 'danger')
                return redirect(request.url)

        rubro = Rubro.query.get(rubro_id)
        latitud = float(latitud) if latitud else None
        longitud = float(longitud) if longitud else None

        nuevo = Proveedor(
            nombre=nombre,
            email=email,
            rubro=rubro,
            descripcion=descripcion,
            telefono=telefono,
            direccion=direccion,
            latitud=latitud,
            longitud=longitud,
            foto_nombre=foto_nombre,
            emergencia=emergencia,
            atencion_24hs=atencion_24hs
        )

        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for('sesion_bp.login_proveedor'))

    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()
    return render_template('agregar_proveedor.html', rubros=rubros)


@proveedores_bp.route('/editar_mi_perfil', methods=['POST'])
def editar_mi_perfil():
    proveedor_id = session.get('proveedor_id')
    if not proveedor_id:
        return redirect(url_for('sesion_bp.login_proveedor'))

    proveedor = Proveedor.query.get_or_404(proveedor_id)
    foto = request.files.get('imagen')  # ← nombre del input en el formulario
    upload_folder = current_app.config['UPLOAD_FOLDER']

    ok, mensaje = procesar_imagen_proveedor(proveedor, foto, upload_folder)

    if not ok and foto and foto.filename != '':
        flash(mensaje, 'danger')
        return redirect(url_for('proveedores_bp.mi_pagina'))

    db.session.commit()
    flash('Logo actualizado correctamente.')
    return redirect(url_for('proveedores_bp.mi_pagina'))


@proveedores_bp.route('/')
def ver_proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre.asc()).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })

    return render_template('listar_proveedores.html', proveedores=proveedores_con_iconos)


@proveedores_bp.route('/proveedor/<int:id>')
def ver_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    productos = Producto.query.filter_by(proveedor_id=id).all()
    opiniones = OpinionProveedor.query.filter_by(proveedor_id=id).order_by(OpinionProveedor.fecha.desc()).all()

    icono_info = rubro_iconos.get(proveedor.rubro.nombre, {'icono': 'bi-shop', 'color': 'text-muted'})

    return render_template('ver_proveedor.html',
                        proveedor=proveedor,
                        productos=productos,
                        opiniones=opiniones,
                        icono=icono_info['icono'],
                        color=icono_info['color'])


from models.proveedor import Proveedor

@proveedores_bp.route('/mi_pagina')
def mi_pagina():
    proveedor_id = session.get('proveedor_id')
    if not proveedor_id:
        flash('No estás logueado como proveedor.')
        return redirect(url_for('sesion_bp.login_proveedor'))

    proveedor = Proveedor.query.get(proveedor_id)
    return render_template('mi_pagina.html', proveedor=proveedor)