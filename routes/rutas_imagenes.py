from flask import Blueprint, request, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
import os
from utils.utils_imagenes import allowed_file, is_valid_mime, validate_image, convert_to_webp

imagenes_bp = Blueprint('imagenes', __name__)

@imagenes_bp.route('/subir_imagen', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        flash('No se encontró el archivo.')
        return redirect(request.url)

    file = request.files['imagen']

    if file.filename == '':
        flash('Nombre de archivo vacío.')
        return redirect(request.url)

    if file and allowed_file(file.filename) and is_valid_mime(file.stream):
        # Convertir y guardar como WebP
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename = convert_to_webp(file.stream, upload_folder)
        file_path = os.path.join(upload_folder, filename)

        # Validar imagen final
        es_valida, mensaje = validate_image(file_path)
        if not es_valida:
            os.remove(file_path)
            flash(mensaje)
            return redirect(request.url)

        # Guardar nombre en la base de datos (ejemplo)
        # proveedor.foto_nombre = filename
        # db.session.commit()

        flash('Imagen subida y validada correctamente.')
        return redirect(url_for('proveedores_bp.mi_pagina'))  # Ajustá según tu vista final

    else:
        flash('Archivo no permitido o tipo MIME inválido.')
        return redirect(request.url)