from flask import Blueprint, request, redirect, url_for, render_template, session, flash, current_app
from models.proveedor import Proveedor
from models.producto import Producto
from models.rubro import Rubro
from models.opiniones import OpinionProducto, OpinionProveedor
from extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func
from utils.rubro_iconos import rubro_iconos
from utils.utils_imagenes import allowed_file, is_valid_mime, validate_image, convert_to_webp
import os


routes_bp = Blueprint('routes_bp', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes_bp.route('/agregar_proveedor', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        # 1. Obtener datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        rubro_id = request.form['rubro_id']  # ← ID del rubro seleccionado
        descripcion = request.form['descripcion']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        password = request.form['password']
        emergencia = bool(request.form.get('emergencia'))
        atencion_24hs = bool(request.form.get('atencion_24hs'))

        # 2. Procesar imagen
        foto = request.files.get('foto')
        foto_nombre = None

        if foto and allowed_file(foto.filename):
            filename = secure_filename(f"{nombre}_{foto.filename}")
            foto.save(os.path.join('static/img_proveedores', filename))
            foto_nombre = filename

        # 3. Obtener el rubro desde la base
        rubro = Rubro.query.get(rubro_id)

        # Validación y conversión
        latitud = float(latitud) if latitud else None
        longitud = float(longitud) if longitud else None


        # 4. Crear proveedor
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

        # 5. Guardar contraseña
        nuevo.set_password(password)

        # 6. Guardar en la base de datos
        db.session.add(nuevo)
        db.session.commit()

        # 7. Redirigir al login
        return redirect(url_for('routes_bp.panel_admin'))

    # Si es GET, mostrar el formulario con rubros disponibles
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()
    return render_template('agregar_proveedor.html', rubros=rubros)


@routes_bp.route('/proveedores')
def ver_proveedores():
    proveedores = Proveedor.query.order_by(Proveedor.nombre.asc()).all()

    # Enriquecer cada proveedor con su ícono
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


@routes_bp.route('/proveedor/<int:id>')
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


@routes_bp.route('/login_proveedor', methods=['GET', 'POST'])
def login_proveedor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print("🔍 Email recibido:", email)
        print("🔍 Contraseña recibida:", password)

        proveedor = Proveedor.query.filter_by(email=email).first()

        if proveedor:
            print("✅ Proveedor encontrado:", proveedor.email)
            print("🔐 Hash en base:", proveedor.password_hash)
            resultado = proveedor.check_password(password)
            print("🔐 Resultado check_password:", resultado)

            if resultado:
                session['proveedor_id'] = proveedor.id
                print("✅ Login exitoso. ID:", proveedor.id)
                return redirect(url_for('routes_bp.mi_pagina'))
            else:
                print("❌ Contraseña incorrecta")
        else:
            print("❌ No se encontró proveedor con ese email")

        return "⚠️ Email o contraseña incorrectos."

    return render_template('login_proveedor.html')


@routes_bp.route('/buscar_por_rubro')
def buscar_por_rubro():
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()
    return render_template('buscar_por_rubro.html', rubros=rubros)


@routes_bp.route('/resultado_rubro')
def resultado_rubro():
    rubro_nombre = request.args.get('rubro')
    proveedores = Proveedor.query.join(Rubro).filter(Rubro.nombre == rubro_nombre).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })


    return render_template('resultado_rubro.html', proveedores=proveedores_con_iconos, rubro=rubro_nombre)


@routes_bp.route('/emergencias')
def ver_emergencias():
    proveedores = Proveedor.query.filter_by(emergencia=True).order_by(Proveedor.nombre.asc()).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })


    return render_template('emergencias.html', proveedores=proveedores_con_iconos)


@routes_bp.route('/atencion_24hs')
def ver_24hs():
    proveedores = Proveedor.query.filter_by(atencion_24hs=True).order_by(Proveedor.nombre.asc()).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })


    return render_template('atencion_24hs.html', proveedores=proveedores_con_iconos)


@routes_bp.route('/admin/editar_proveedor/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    if not session.get('es_admin'):
        return redirect(url_for('routes_bp.login'))

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

        foto = request.files['foto']
        if foto and foto.filename != '':
            nombre_archivo = secure_filename(foto.filename)
            foto.save(os.path.join('static/img_proveedores', nombre_archivo))
            proveedor.foto_nombre = nombre_archivo

        db.session.commit()
        return redirect(url_for('routes_bp.panel_admin'))

    return render_template('editar_proveedor.html', proveedor=proveedor, rubros=rubros)


@routes_bp.route('/admin/eliminar_proveedor/<int:id>')
def eliminar_proveedor(id):
    if not session.get('es_admin'):
        return redirect(url_for('routes_bp.login'))

    proveedor = Proveedor.query.get_or_404(id)

    # Eliminar imagen asociada si existe
    if proveedor.foto_nombre:
        ruta_imagen = os.path.join('static/img_proveedores', proveedor.foto_nombre)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Eliminar productos asociados (si querés hacerlo en cascada)
    productos = Producto.query.filter_by(proveedor_id=proveedor.id).all()
    for producto in productos:
        db.session.delete(producto)

    db.session.delete(proveedor)
    db.session.commit()
    return redirect(url_for('routes_bp.panel_admin'))

# -------------------------------------------------------------------------------------------------------------
@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']

        admin_user = os.getenv('ADMIN_USER')
        admin_pass = os.getenv('ADMIN_PASS')

        if usuario == admin_user and clave == admin_pass:
            session['es_admin'] = True
            return redirect(url_for('routes_bp.panel_admin'))
        else:
            flash('Credenciales incorrectas', 'danger')
            return redirect(url_for('routes_bp.login'))

    return render_template('login.html')


@routes_bp.route('/logout')
def logout():
    session.pop('es_admin', None)
    return redirect(url_for('routes_bp.index'))


@routes_bp.route('/admin')
def panel_admin():
    if not session.get('es_admin'):
        return redirect(url_for('routes_bp.login'))

    proveedores = Proveedor.query.all()
    productos = Producto.query.all()
    return render_template('panel_admin.html',
                        proveedores=proveedores,
                        productos=productos)


@routes_bp.route('/')
def index():
    ahora = datetime.utcnow()
    hace_5_dias = ahora - timedelta(days=5)

    todos = Proveedor.query.all()
    print("Hoy:", ahora)
    print("Hace 5 días:", hace_5_dias)
    for p in todos:
        print(p.nombre, p.fecha_registro, "→", (ahora - p.fecha_registro).total_seconds(), "segundos atrás")

    nuevos_proveedores = Proveedor.query.filter(Proveedor.fecha_registro >= hace_5_dias).all()
    print("Cantidad de nuevos proveedores:", len(nuevos_proveedores))

    return render_template('index.html', nuevos_proveedores=nuevos_proveedores)


@routes_bp.route('/mi_pagina')
def mi_pagina():
    if 'proveedor_id' not in session:
        return redirect(url_for('routes_bp.login_proveedor'))
    proveedor = Proveedor.query.get(session['proveedor_id'])
    return render_template('mi_pagina.html', proveedor=proveedor)

#----------------------------------------------------------------------------------------------------------------

@routes_bp.route('/subir_producto', methods=['POST'])
def subir_producto():
    if 'proveedor_id' not in session:
        return redirect(url_for('routes_bp.login_proveedor'))

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    foto = request.files['foto']

    if not foto or foto.filename == '':
        flash('No se seleccionó ninguna imagen.')
        return redirect(url_for('routes_bp.mi_pagina'))

    # Validar extensión y tipo MIME
    if not allowed_file(foto.filename) or not is_valid_mime(foto.stream):
        flash('Formato de imagen no permitido.')
        return redirect(url_for('routes_bp.mi_pagina'))

    # Convertir y guardar como WebP
    upload_folder = current_app.config['UPLOAD_FOLDER_PRODUCTOS']
    filename = convert_to_webp(foto.stream, upload_folder)
    file_path = os.path.join(upload_folder, filename)

    # Validar dimensiones y peso
    es_valida, mensaje = validate_image(file_path)
    if not es_valida:
        os.remove(file_path)
        flash(mensaje)
        return redirect(url_for('routes_bp.mi_pagina'))

    # Crear y guardar el producto
    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        foto_nombre=filename,
        proveedor_id=session['proveedor_id']
    )
    db.session.add(nuevo_producto)
    db.session.commit()

    flash('Producto subido correctamente.')
    return redirect(url_for('routes_bp.mi_pagina'))


@routes_bp.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if 'proveedor_id' not in session:
        return redirect('/login')
    
    producto = Producto.obtener_producto_por_id(id)
    if producto.proveedor_id != session['proveedor_id']:
        return "Acceso no autorizado", 403
    
    print("Intentando eliminar imagen:", producto.foto_nombre)

    # Eliminar imagen asociada si existe
    if producto.foto_nombre:
        ruta_imagen = os.path.abspath(os.path.join('static', 'img_productos', producto.foto_nombre))
        if os.path.exists(ruta_imagen):
            try:
                os.remove(ruta_imagen)
                print(f"Imagen eliminada: {ruta_imagen}")
            except Exception as e:
                print(f"No se pudo eliminar la imagen: {e}")

    Producto.eliminar_producto_por_id(id)
    return redirect('/mi_pagina')


@routes_bp.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'proveedor_id' not in session:
        return redirect('/login')
    
    producto = Producto.obtener_producto_por_id(id)
    if producto.proveedor_id != session['proveedor_id']:
        return "Acceso no autorizado", 403

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nueva_descripcion = request.form['descripcion']

        # Manejo de imagen nueva
        foto = request.files.get('foto')
        if foto and foto.filename != '':
            nombre_archivo = secure_filename(foto.filename)
            ruta_imagen = os.path.join('static/img_productos', nombre_archivo)
            foto.save(ruta_imagen)

            # Eliminar imagen anterior si existe
            if producto.foto_nombre:
                ruta_anterior = os.path.abspath(os.path.join('static', 'img_productos', producto.foto_nombre))
            if os.path.exists(ruta_anterior):
                try:
                    os.remove(ruta_anterior)
                    print(f"Imagen anterior eliminada: {ruta_anterior}")
                except Exception as e:
                    print(f"No se pudo eliminar la imagen anterior: {e}")

            producto.foto_nombre = nombre_archivo

        producto.nombre = nuevo_nombre
        producto.descripcion = nueva_descripcion
        db.session.commit()

        return redirect('/mi_pagina')

    return render_template('editar_producto.html', producto=producto, origen='proveedor')


from models.opiniones import OpinionProducto

@routes_bp.route('/ver_producto/<int:id>')
def ver_producto(id):
    producto = Producto.query.get_or_404(id)
    opiniones = OpinionProducto.query.filter_by(producto_id=id).order_by(OpinionProducto.fecha.desc()).all()
    return render_template('ver_producto.html', producto=producto, opiniones=opiniones)


@routes_bp.route('/admin/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto_admin(id):
    if not session.get('es_admin'):
        return redirect(url_for('routes_bp.login'))

    producto = Producto.query.get_or_404(id)
    proveedores = Proveedor.query.all()

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.proveedor_id = request.form['proveedor_id']

        imagen = request.files.get('foto')
        if imagen and imagen.filename != '':
            nombre_archivo = secure_filename(imagen.filename)
            imagen.save(os.path.join('static/img_productos', nombre_archivo))
            producto.imagen_nombre = nombre_archivo

        db.session.commit()
        return redirect(url_for('routes_bp.panel_admin'))

    return render_template('editar_producto.html', producto=producto, proveedores=proveedores, origen='admin')


@routes_bp.route('/admin/eliminar_producto/<int:id>')
def eliminar_producto_admin(id):
    if not session.get('es_admin'):
        return redirect(url_for('routes_bp.login'))

    producto = Producto.query.get_or_404(id)

    # Eliminar imagen asociada si existe
    if producto.foto_nombre:
        ruta_imagen = os.path.join('static/img_productos', producto.foto_nombre)
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('routes_bp.panel_admin'))