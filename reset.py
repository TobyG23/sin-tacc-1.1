from app import app, db
from models import LugarSugerido

with app.app_context():
    aprobadas = LugarSugerido.query.filter_by(aprobado=True).all()
    for lugar in aprobadas:
        db.session.delete(lugar)
    db.session.commit()
    print("🧽 Se eliminaron las sugerencias aprobadas.")
