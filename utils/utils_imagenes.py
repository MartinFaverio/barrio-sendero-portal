import os
from PIL import Image
import uuid

# Configuración sagrada
MAX_WIDTH = 800
MAX_HEIGHT = 800
MAX_FILE_SIZE = 300 * 1024  # 300 KB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_mime(file_storage):
    try:
        with Image.open(file_storage) as img:
            formato = img.format.lower()  # 'jpeg', 'png', 'webp', etc.
            return formato in ALLOWED_EXTENSIONS
    except Exception:
        return False

def validate_image(file_path):
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return False, "La imagen supera los 300 KB."

    with Image.open(file_path) as img:
        width, height = img.size
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            return False, f"Dimensiones demasiado grandes: {width}x{height}px."

    return True, "Imagen válida."

def convert_to_webp(file_storage, output_folder, max_size=(800, 800)):
    image = Image.open(file_storage)
    image = image.convert("RGB")
    image.thumbnail(max_size)

    filename = f"{uuid.uuid4().hex}.webp"
    path = os.path.join(output_folder, filename)
    image.save(path, format='WEBP', quality=85)

    return filename


def procesar_imagen_proveedor(proveedor, foto, upload_folder):
    if not foto or foto.filename == '' or not allowed_file(foto.filename) or not is_valid_mime(foto):
        return False, "Archivo inválido o no permitido."

    nuevo_nombre = convert_to_webp(foto, upload_folder)
    ruta_nueva = os.path.join(upload_folder, nuevo_nombre)

    es_valida, mensaje = validate_image(ruta_nueva)
    if not es_valida:
        os.remove(ruta_nueva)
        return False, mensaje

    anterior_nombre = proveedor.foto_nombre
    if anterior_nombre:
        ruta_anterior = os.path.join(upload_folder, anterior_nombre)
        if os.path.exists(ruta_anterior):
            try:
                os.remove(ruta_anterior)
                print(f"🔥 Imagen anterior eliminada: {ruta_anterior}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar la imagen anterior: {e}")

    proveedor.foto_nombre = nuevo_nombre
    print(f"✅ Imagen nueva asignada: {nuevo_nombre}")
    return True, "Imagen procesada correctamente."