from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime

db = SQLAlchemy()

class LugarSugerido(db.Model):
    __tablename__ = 'lugar_sugerido'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String, nullable=False)
    provincia = db.Column(db.String, nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    comentarios = db.Column(db.Text)
    aprobado = db.Column(db.Boolean, default=False)
    rechazado = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.Date, default=date.today)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    destacado = db.Column(db.Boolean, default=False)


    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "tipo": self.tipo,
            "comentarios": self.comentarios,
            "aprobado": self.aprobado,
            "fecha_envio": str(self.fecha_envio) if self.fecha_envio else None,
            "lat": self.lat,
            "lng": self.lng
        }

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

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
