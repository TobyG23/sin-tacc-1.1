from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime

db = SQLAlchemy()

# Tablas de asociación many-to-many
lugar_categorias = db.Table('lugar_categorias',
    db.Column('lugar_id', db.Integer, db.ForeignKey('lugar_sugerido.id'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categorias.id'), primary_key=True)
)

lugar_etiquetas = db.Table('lugar_etiquetas',
    db.Column('lugar_id', db.Integer, db.ForeignKey('lugar_sugerido.id'), primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas_especiales.id'), primary_key=True)
)

class LugarSugerido(db.Model):
    __tablename__ = 'lugar_sugerido'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)  # Nueva: descripción del comercio
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String, nullable=False)
    provincia = db.Column(db.String, nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Mantener por compatibilidad
    telefono = db.Column(db.String(20))  # Nueva
    email_contacto = db.Column(db.String(150))  # Nueva
    sitio_web = db.Column(db.String(200))  # Nueva
    comentarios = db.Column(db.Text)
    aprobado = db.Column(db.Boolean, default=False)
    rechazado = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.Date, default=date.today)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    destacado = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    banner_url = db.Column(db.String(255))

    # Campos de analytics
    vistas = db.Column(db.Integer, default=0)  # Nueva
    clics_como_llegar = db.Column(db.Integer, default=0)  # Nueva
    clics_telefono = db.Column(db.Integer, default=0)  # Nueva

    # Horarios (guardado como JSON string)
    horarios = db.Column(db.Text)  # Nueva: JSON con horarios por día

    # Relaciones
    usuario = db.relationship('Usuario', backref='lugar_asociado')
    categorias = db.relationship('Categoria', secondary=lugar_categorias, backref='lugares')
    etiquetas = db.relationship('EtiquetaEspecial', secondary=lugar_etiquetas, backref='lugares')
    menus = db.relationship('Menu', backref='lugar', lazy='dynamic', cascade='all, delete-orphan')
    redes_sociales = db.relationship('RedSocial', backref='lugar', lazy='dynamic', cascade='all, delete-orphan')
    fotos = db.relationship('FotoLugar', backref='lugar', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "pais": self.pais,
            "tipo": self.tipo,
            "telefono": self.telefono,
            "email_contacto": self.email_contacto,
            "sitio_web": self.sitio_web,
            "comentarios": self.comentarios,
            "aprobado": self.aprobado,
            "fecha_envio": str(self.fecha_envio) if self.fecha_envio else None,
            "lat": self.lat,
            "lng": self.lng,
            "destacado": self.destacado,
            "vistas": self.vistas,
            "categorias": [cat.nombre for cat in self.categorias],
            "etiquetas": [et.nombre for et in self.etiquetas]
        }

class Categoria(db.Model):
    """Categorías de comercios (Restaurante, Cafetería, Panadería, etc.)"""
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)  # Para URLs
    icono = db.Column(db.String(50))  # Nombre del icono (ej: 'restaurant', 'coffee')
    color = db.Column(db.String(7), default='#3388ff')  # Color hex para el pin
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)  # Para ordenar en filtros

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class EtiquetaEspecial(db.Model):
    """Etiquetas especiales (Sin Gluten, Vegano, Vegetariano, etc.)"""
    __tablename__ = 'etiquetas_especiales'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    icono = db.Column(db.String(50))  # Nombre del icono
    color = db.Column(db.String(7), default='#28a745')  # Color hex
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<EtiquetaEspecial {self.nombre}>'

class Menu(db.Model):
    """Menús/Cartas de los comercios"""
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar_sugerido.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)  # "Menú Principal", "Carta de Vinos"
    descripcion = db.Column(db.Text)
    archivo_url = db.Column(db.String(300))  # URL del PDF/imagen del menú completo
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con items
    items = db.relationship('ItemMenu', backref='menu', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Menu {self.nombre} - {self.lugar_id}>'

class ItemMenu(db.Model):
    """Items individuales dentro de un menú"""
    __tablename__ = 'items_menu'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float)
    categoria_item = db.Column(db.String(50))  # Entrada, Principal, Postre, Bebida, etc.
    imagen_url = db.Column(db.String(300))
    disponible = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    # Etiquetas del item (puede tener etiquetas especiales)
    # Guardado como string separado por comas: "sin gluten,vegano,picante"
    etiquetas_item = db.Column(db.String(200))

    def __repr__(self):
        return f'<ItemMenu {self.nombre}>'

class RedSocial(db.Model):
    """Redes sociales y códigos QR de los comercios"""
    __tablename__ = 'redes_sociales'

    id = db.Column(db.Integer, primary_key=True)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar_sugerido.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # facebook, instagram, whatsapp, etc.
    url_perfil = db.Column(db.String(300), nullable=False)
    qr_code_url = db.Column(db.String(300))  # URL de la imagen del QR generado
    activo = db.Column(db.Boolean, default=True)
    clics = db.Column(db.Integer, default=0)  # Analytics: cuántos clics recibió
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RedSocial {self.tipo} - {self.lugar_id}>'

class FotoLugar(db.Model):
    """Galería de fotos de los comercios"""
    __tablename__ = 'fotos_lugar'

    id = db.Column(db.Integer, primary_key=True)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar_sugerido.id'), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    descripcion = db.Column(db.String(200))
    es_principal = db.Column(db.Boolean, default=False)  # Foto principal del comercio
    orden = db.Column(db.Integer, default=0)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FotoLugar {self.id} - {self.lugar_id}>'

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    es_comercio = db.Column(db.Boolean, default=False)
    nombre_comercio = db.Column(db.String(100))
    ya_registrado_en_mapa = db.Column(db.Boolean, default=False)
    dono = db.Column(db.Boolean, default=False)
    publicidad_activa = db.Column(db.Boolean, default=True)

    # Nuevos campos para comercios
    plan = db.Column(db.String(20), default='gratuito')  # gratuito, destacado, premium
    fecha_expiracion_plan = db.Column(db.Date)  # Para planes pagos

    def __repr__(self):
        return f'<Usuario {self.email}>'

class LogAccion(db.Model):
    __tablename__ = 'logs_acciones'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_afectado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("Usuario", foreign_keys=[admin_id], backref="acciones_realizadas")
    usuario_afectado = db.relationship("Usuario", foreign_keys=[usuario_afectado_id], backref="acciones_recibidas")

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    puntuacion = db.Column(db.Integer, nullable=False)  # de 1 a 5
    comentario = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar_sugerido.id'), nullable=False)

    usuario = db.relationship('Usuario', backref='reviews')
    lugar = db.relationship('LugarSugerido', backref='reviews')

class BannerPublicidad(db.Model):
    __tablename__ = 'banners_publicidad'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(300))
    imagen_url = db.Column(db.String(300))
    activo = db.Column(db.Boolean, default=True)
    creado = db.Column(db.DateTime, default=datetime.utcnow)
