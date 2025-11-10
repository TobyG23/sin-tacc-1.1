"""
Utilidades y servicios auxiliares para LocalHub
"""
import qrcode
from io import BytesIO
import os
from werkzeug.utils import secure_filename
from PIL import Image

def generate_qr_code(data, filename=None, save_path='static/qr_codes'):
    """
    Genera un código QR a partir de los datos proporcionados

    Args:
        data (str): Datos a codificar en el QR (URL, texto, etc.)
        filename (str): Nombre del archivo (opcional, se genera automáticamente si no se provee)
        save_path (str): Ruta donde guardar el QR

    Returns:
        str: Ruta relativa del archivo QR generado
    """
    # Crear directorio si no existe
    os.makedirs(save_path, exist_ok=True)

    # Generar QR
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")

    # Generar nombre de archivo si no se proporcionó
    if not filename:
        import hashlib
        hash_data = hashlib.md5(data.encode()).hexdigest()[:10]
        filename = f"qr_{hash_data}.png"
    else:
        filename = secure_filename(filename)
        if not filename.endswith('.png'):
            filename += '.png'

    # Guardar archivo
    filepath = os.path.join(save_path, filename)
    img.save(filepath)

    # Retornar ruta relativa
    return f"qr_codes/{filename}"


def generate_social_qr(lugar_id, tipo, url):
    """
    Genera un QR code para una red social específica de un comercio

    Args:
        lugar_id (int): ID del lugar
        tipo (str): Tipo de red social (facebook, instagram, whatsapp, etc.)
        url (str): URL del perfil

    Returns:
        str: Ruta relativa del QR generado
    """
    filename = f"qr_lugar_{lugar_id}_{tipo}.png"
    return generate_qr_code(url, filename=filename)


def generate_business_card_qr(lugar):
    """
    Genera un QR code con toda la información del comercio (vCard o URL)

    Args:
        lugar (LugarSugerido): Objeto del lugar

    Returns:
        str: Ruta relativa del QR generado
    """
    # Generar URL del perfil del comercio
    from flask import url_for
    url = url_for('ver_lugar', lugar_id=lugar.id, _external=True)

    filename = f"qr_lugar_{lugar.id}_card.png"
    return generate_qr_code(url, filename=filename)


def generate_menu_qr(lugar_id, menu_id):
    """
    Genera un QR code para un menú específico

    Args:
        lugar_id (int): ID del lugar
        menu_id (int): ID del menú

    Returns:
        str: Ruta relativa del QR generado
    """
    from flask import url_for
    # En el futuro, esto podría apuntar a una URL específica del menú
    url = url_for('ver_lugar', lugar_id=lugar_id, _external=True) + f"#menu-{menu_id}"

    filename = f"qr_lugar_{lugar_id}_menu_{menu_id}.png"
    return generate_qr_code(url, filename=filename)


def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif', 'pdf'}):
    """
    Verifica si un archivo tiene una extensión permitida

    Args:
        filename (str): Nombre del archivo
        allowed_extensions (set): Conjunto de extensiones permitidas

    Returns:
        bool: True si la extensión es válida
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, folder, prefix='', max_size_mb=5):
    """
    Guarda un archivo subido y retorna su ruta relativa

    Args:
        file: Archivo de Werkzeug FileStorage
        folder (str): Carpeta destino (ej: 'menus', 'fotos')
        prefix (str): Prefijo para el nombre del archivo
        max_size_mb (int): Tamaño máximo en MB

    Returns:
        str or None: Ruta relativa del archivo guardado o None si hay error
    """
    if not file or file.filename == '':
        return None

    # Verificar tamaño
    file.seek(0, 2)  # Ir al final del archivo
    size = file.tell()
    file.seek(0)  # Volver al inicio

    if size > max_size_mb * 1024 * 1024:
        raise ValueError(f"El archivo excede el tamaño máximo de {max_size_mb}MB")

    # Sanitizar nombre de archivo
    filename = secure_filename(file.filename)

    # Agregar timestamp para evitar sobrescritura
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)

    if prefix:
        filename = f"{prefix}_{timestamp}_{name}{ext}"
    else:
        filename = f"{timestamp}_{name}{ext}"

    # Crear directorio si no existe
    upload_path = os.path.join('static', folder)
    os.makedirs(upload_path, exist_ok=True)

    # Guardar archivo
    filepath = os.path.join(upload_path, filename)
    file.save(filepath)

    # Retornar ruta relativa
    return f"{folder}/{filename}"


def optimize_image(filepath, max_width=1200, max_height=1200, quality=85):
    """
    Optimiza una imagen reduciendo su tamaño si es necesario

    Args:
        filepath (str): Ruta completa del archivo
        max_width (int): Ancho máximo
        max_height (int): Alto máximo
        quality (int): Calidad de compresión (1-100)

    Returns:
        bool: True si se optimizó correctamente
    """
    try:
        with Image.open(filepath) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Redimensionar si es necesario
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Guardar con compresión
            img.save(filepath, 'JPEG', quality=quality, optimize=True)

        return True
    except Exception as e:
        print(f"Error optimizando imagen: {e}")
        return False


def format_price(price):
    """
    Formatea un precio para mostrar

    Args:
        price (float): Precio numérico

    Returns:
        str: Precio formateado (ej: "$1,234.56")
    """
    if price is None:
        return "N/A"

    return f"${price:,.2f}"


def parse_horarios(horarios_json):
    """
    Parsea el JSON de horarios y retorna un diccionario

    Args:
        horarios_json (str): JSON string con horarios

    Returns:
        dict: Diccionario con horarios por día
    """
    import json

    if not horarios_json:
        return {}

    try:
        return json.loads(horarios_json)
    except:
        return {}


def format_horarios(horarios_dict):
    """
    Convierte un diccionario de horarios a JSON string

    Args:
        horarios_dict (dict): Diccionario con horarios

    Returns:
        str: JSON string
    """
    import json
    return json.dumps(horarios_dict, ensure_ascii=False)
