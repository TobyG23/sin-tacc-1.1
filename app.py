import requests
import csv
import os
from dotenv import load_dotenv
load_dotenv()
from flask import send_from_directory
from PIL import Image
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, abort, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from markupsafe import escape
from models import db, LugarSugerido, Usuario, Review, Menu, ItemMenu, Categoria, EtiquetaEspecial, RedSocial, FotoLugar, BannerPublicidad, LogAccion
import utils
from datetime import datetime
from sqlalchemy import func
from functools import wraps





def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)

clave_secreta = os.getenv('SECRET_KEY')
if not clave_secreta:
    raise RuntimeError("SECRET_KEY no encontrada en variables de entorno.")
app.secret_key = clave_secreta


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_NdKPSa7rQ1et@ep-snowy-thunder-a4gsx6gn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'glutymap.info@gmail.com'  # Cambiá por el tuyo
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Ideal usar clave de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'glutymap.info@gmail.com'

mail = Mail(app)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route('/mapa')
def ver_mapa():
    resultados = db.session.query(
        LugarSugerido,
        func.avg(Review.puntuacion).label("promedio")
    ).outerjoin(Review).group_by(LugarSugerido.id).all()

    lugares = []
    for lugar, promedio in resultados:
        lugares.append({
            'id': lugar.id,
            'nombre': lugar.nombre,
            'direccion': lugar.direccion,
            'ciudad': lugar.ciudad,
            'provincia': lugar.provincia,
            'lat': lugar.lat,
            'lng': lugar.lng,
            'tipo': lugar.tipo,
            'promedio': round(promedio or 0, 1),
            'destacado': lugar.destacado
        })

    return render_template("mapa.html", lugares=lugares)



@app.route('/sugerir', methods=['GET', 'POST'])
@login_required
def sugerir():
        if request.method == 'POST':
            print(request.form)

            nombre = escape(request.form.get('nombre', '')).strip()
            direccion = escape(request.form.get('direccion', '')).strip()
            ciudad = escape(request.form.get('ciudad', '')).strip()
            provincia = escape(request.form.get('provincia', '')).strip()
            pais = escape(request.form.get('pais', '')).strip()
            tipo = escape(request.form.get('tipo', '')).strip()
            comentarios = escape(request.form.get('comentarios', '')).strip()

            nombre_mapa = escape(request.form.get('nombre_mapa', '')).strip()
            tipo_mapa = escape(request.form.get('tipo_mapa', '')).strip()
            comentarios_mapa = escape(request.form.get('comentarios_mapa', '')).strip()

            lat = request.form.get('lat')
            lng = request.form.get('lng')

            errores = []

            if not lat and not lng:
                if len(nombre) < 3:
                    errores.append('El nombre debe tener al menos 3 caracteres.')
                if len(direccion) < 3:
                    errores.append('La direccion debe tener al menos 3 caracteres.')
                if len(ciudad) < 3:
                    errores.append('La ciudad debe tener al menos 3 caracteres.')
                if len(provincia) < 3:
                    errores.append('La provincia debe tener al menos 3 caracteres.')
                if len(tipo) < 3:
                    errores.append("El tipo de comercio debe tener al menos 3 caracteres.")
            else:
                if len(nombre_mapa) < 3:
                    errores.append("El nombre del comercio (por mapa) debe tener al menos 3 caracteres.")
                if len(tipo_mapa) < 3:
                    errores.append("El tipo de comercio (por mapa) debe tener al menos 3 caracteres.")

            if comentarios and len(comentarios) > 500:
                errores.append("El comentario es demasiado largo (máx. 500 caracteres).")
            if comentarios_mapa and len(comentarios_mapa) > 500:
                errores.append("El comentario del mapa es demasiado largo (máx. 500 caracteres).")

            if errores:
                for error in errores:
                    flash("❌ " + error, 'danger')
                return redirect(url_for('sugerir'))

            if lat == '' or lat is None:
                lat = None
            if lng == '' or lng is None:
                lng = None

            try:
                lat = float(lat) if lat else None
                lng = float(lng) if lng else None
            except ValueError:
                lat, lng = None, None

            usando_mapa = lat is not None and lng is not None

            if usando_mapa:
                if not nombre_mapa or not tipo_mapa:
                    flash('❌ Todos los campos obligatorios deben completarse.', 'danger')
                    return redirect(url_for('sugerir'))
            else:
                if not nombre or not direccion or not ciudad or not provincia or not pais or not tipo:
                    flash('❌ Todos los campos obligatorios deben completarse.', 'danger')
                    return redirect(url_for('sugerir'))

                # 🔍 Geocodificación automática
                direccion_completa = f"{direccion}, {ciudad}, {provincia}, {pais}"
                lat, lng = geocodificar_direccion(direccion_completa)
                if lat is None or lng is None:
                    flash("⚠️ No se pudo geolocalizar la dirección automáticamente. Por favor completá la ubicación manualmente desde el panel de revisión.", "warning")
                    return redirect(url_for('ver_mapa'))


            nuevo_lugar = LugarSugerido(
                nombre=nombre_mapa if usando_mapa else nombre,
                direccion=direccion if not usando_mapa else 'Ubicación seleccionada en mapa',
                ciudad=ciudad if not usando_mapa else '',
                provincia=provincia if not usando_mapa else '',
                pais=pais,
                tipo=tipo_mapa if usando_mapa else tipo,
                comentarios=comentarios_mapa if usando_mapa else comentarios,
                lat=lat,
                lng=lng
            )

            db.session.add(nuevo_lugar)
            db.session.commit()

            try:
                msg = Message("📩 ¡Tu sugerencia fue recibida!", recipients=[current_user.email])
                msg.body = f"""
            Hola {current_user.email} 👋

            Tu sugerencia para agregar el lugar "{nuevo_lugar.nombre}" ha sido recibida exitosamente en GlutyMap 🎉

            📌 Dirección: {nuevo_lugar.direccion}, {nuevo_lugar.ciudad}, {nuevo_lugar.provincia}, {nuevo_lugar.pais}
            🏷️ Tipo: {nuevo_lugar.tipo}

            Nuestro equipo la revisará pronto y te avisaremos si es aprobada ✅

            Gracias por sumar al mapa 🌍

            — GlutyMap Team
            """
                mail.send(msg)
            except Exception as e:
                print("❌ Error al enviar confirmación al usuario:", e)



            return redirect(url_for('ver_mapa', enviado='ok'))
        
        # Si el método no fue POST, simplemente renderiza el formulario
        return render_template('formulario.html')




@app.route('/lugar/<int:id>/destacar', methods=['POST'])
@login_required
@admin_required
def destacar_lugar(id):
    lugar = LugarSugerido.query.get_or_404(id)
    lugar.destacado = True
    db.session.commit()

    return redirect(url_for('revisar_lugares'))

@app.route('/lugar/<int:id>/quitar_destacado', methods=['POST'])
@login_required
@admin_required
def quitar_destacado(id):
    lugar = LugarSugerido.query.get_or_404(id)
    lugar.destacado = False
    db.session.commit()
    return redirect(url_for('revisar_lugares'))


#Sistema de reviews
@app.route('/lugar/<int:lugar_id>', methods=['GET', 'POST'])
def ver_lugar(lugar_id):
    lugar = LugarSugerido.query.get_or_404(lugar_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Necesitás iniciar sesión para dejar una review.", "warning")
            return redirect(url_for('login'))

        puntuacion = int(request.form.get('puntuacion'))
        comentario = request.form.get('comentario')

        nueva_review = Review(
            puntuacion=puntuacion,
            comentario=comentario,
            usuario_id=current_user.id,
            lugar_id=lugar.id,
            fecha=datetime.utcnow()
        )
        db.session.add(nueva_review)
        db.session.commit()
        flash("✅ Review enviada con éxito", "success")
        return redirect(url_for('ver_lugar', lugar_id=lugar.id))

    reviews = Review.query.filter_by(lugar_id=lugar.id).order_by(Review.fecha.desc()).all()
    return render_template('ver_lugar.html', lugar=lugar, reviews=reviews)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        es_comercio = request.form.get("es_comercio") == "true"
        nombre_comercio = request.form.get("nombre_comercio") if es_comercio else None
        ya_registrado = request.form.get("ya_registrado") if es_comercio else None


        if Usuario.query.filter_by(email=email).first():
            flash('❌ El correo ya está registrado.', 'danger')
            return redirect(url_for('register'))

        hash = generate_password_hash(password)
        nuevo_usuario = Usuario(
        email=email,
        password=hash,
        es_comercio=es_comercio,
        nombre_comercio=nombre_comercio,
        ya_registrado_en_mapa=(ya_registrado == "si")
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        login_user(nuevo_usuario)
        flash('👤 Usuario creado exitosamente.', 'success')
        return redirect(url_for('ver_mapa'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not check_password_hash(usuario.password, password):
            flash('❌ Email o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))

        login_user(usuario)
        flash('👋 Bienvenido nuevamente.', 'success')
        return redirect(url_for('ver_mapa'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    flash('🚪 Cerraste sesión exitosamente.', 'info')
    logout_user()
    return redirect(url_for('ver_mapa'))

# Reemplazo completo de la ruta /dashboard por una vista mejorada en /revisar
@app.route('/revisar')
@login_required
def revisar_lugares():
    if not current_user.is_admin:
        abort(403)

    estado = request.args.get('estado')  # pendiente / aprobado / rechazado
    filtro_pais = request.args.get('pais', '').strip().lower()
    filtro_nombre = request.args.get('nombre', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 6

    query = LugarSugerido.query

    if estado == 'pendiente':
        query = query.filter_by(aprobado=False, rechazado=False)
    elif estado == 'aprobado':
        query = query.filter_by(aprobado=True, rechazado=False)
    elif estado == 'rechazado':
        query = query.filter_by(rechazado=True)

    if filtro_pais:
        query = query.filter(LugarSugerido.pais.ilike(f"%{filtro_pais}%"))

    if filtro_nombre:
        query = query.filter(LugarSugerido.nombre.ilike(f"%{filtro_nombre}%"))

    lugares = query.order_by(LugarSugerido.fecha_envio.desc()).paginate(page=page, per_page=per_page)

    return render_template('revisar.html', lugares=lugares, estado=estado, filtro_pais=filtro_pais, filtro_nombre=filtro_nombre)



@app.route('/mi-comercio')
@login_required
def mi_comercio():
    if not current_user.es_comercio:
        flash("⚠️ Esta sección es solo para comercios.", "warning")
        return redirect(url_for('ver_mapa'))

    lugar = LugarSugerido.query.filter_by(usuario_id=current_user.id).first()
    promedio = None

    if lugar:
        reviews = lugar.reviews
        if reviews:
            promedio = round(sum(r.puntuacion for r in reviews) / len(reviews), 1)

    return render_template("mi_comercio.html", lugar=lugar, promedio=promedio)

@app.route('/mi-comercio/estadisticas')
@login_required
def estadisticas_comercio():
    if not current_user.es_comercio:
        abort(403)

    lugar = LugarSugerido.query.filter_by(usuario_id=current_user.id).first()
    if not lugar:
        flash("No se encontró tu comercio en el mapa.", "warning")
        return redirect(url_for("mi_comercio"))

    reviews = Review.query.filter_by(lugar_id=lugar.id).order_by(Review.fecha.desc()).all()
    promedio = None
    if reviews:
        promedio = round(sum(r.puntuacion for r in reviews) / len(reviews), 1)

    return render_template("estadisticas_comercio.html", lugar=lugar, promedio=promedio, total_reviews=len(reviews), reviews=reviews)

@app.route('/mi-comercio/destacar', methods=['GET', 'POST'])
@login_required
def destacar_comercio():
    if not current_user.es_comercio:
        abort(403)

    lugar = LugarSugerido.query.filter_by(usuario_id=current_user.id).first()

    if not lugar:
        flash("Tu comercio no está vinculado todavía al mapa.", "warning")
        return redirect(url_for("mi_comercio"))

    if request.method == 'POST':
        lugar.destacado = True
        db.session.commit()
        flash("⭐ Tu comercio ahora está destacado en el mapa.", "success")
        return redirect(url_for('mi_comercio'))

    return render_template("destacar_comercio.html", lugar=lugar)

@app.route('/subir-banner', methods=['GET', 'POST'])
@login_required
def subir_banner():
    if not current_user.es_comercio:
        flash("⚠️ Acceso solo para comercios.", "warning")
        return redirect(url_for('ver_mapa'))

    lugar = LugarSugerido.query.filter_by(usuario_id=current_user.id).first_or_404()

    if request.method == 'POST':
        archivo = request.files['banner']
        titulo = request.form.get('titulo_banner')
        titulo = titulo.strip() if titulo and titulo.strip() != '' else None

        link = request.form.get('link_banner', '').strip()

        if archivo:
            filename = secure_filename(archivo.filename)
            path = os.path.join('static/banners', filename)

            try:
                # Validar imagen
                img = Image.open(archivo)
                img.verify()
                archivo.seek(0)
                archivo.save(path)

                # Actualiza el lugar
                lugar.banner_url = filename
                db.session.commit()

                # Crea o actualiza la publicidad
                from models import BannerPublicidad

                titulo_final = titulo if titulo else f"Promoción de {lugar.nombre}"
                link_final = link if link else "#"

                banner_existente = BannerPublicidad.query.filter_by(imagen_url=filename).first()
                if banner_existente:
                    banner_existente.titulo = titulo_final
                    banner_existente.link = link_final
                    banner_existente.activo = True
                else:
                    nuevo_banner = BannerPublicidad(
                        titulo=titulo_final,
                        link=link_final,
                        imagen_url=filename,
                        activo=True
                    )
                    db.session.add(nuevo_banner)

                db.session.commit()
                flash("✅ Banner subido correctamente y promoción activada.", "success")

            except Exception as e:
                flash("❌ El archivo no es una imagen válida.", "danger")
                print("Error al validar la imagen:", e)

            return redirect(url_for('mi_comercio'))

    return render_template('subir_banner.html', lugar=lugar)



@app.route('/admin/quitar_banner/<int:lugar_id>', methods=['POST'])
@login_required
def quitar_banner(lugar_id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.get_or_404(lugar_id)

    # Guardamos la URL antes de borrarla
    banner_url_original = lugar.banner_url

    lugar.banner_url = None
    lugar.destacado = False

    # Buscar el banner correspondiente por la URL guardada
    from models import BannerPublicidad
    banner = BannerPublicidad.query.filter_by(imagen_url=banner_url_original).first()
    if banner:
        banner.activo = False  # 👈 Lo desactivamos

    db.session.commit()
    flash("🚫 Publicidad eliminada del comercio.", "info")
    return redirect(url_for('recomendados'))



@app.context_processor
def inject_banners():
    from models import BannerPublicidad
    try:
        if current_user.is_authenticated:
            if hasattr(current_user, 'publicidad_activa') and not current_user.publicidad_activa:
                return dict(banners=[])
    except:
        pass  # fallback si current_user falla por algún motivo

    banners = BannerPublicidad.query.filter_by(activo=True).all()

    # Convertimos los objetos a diccionarios
    banners_dict = [{
        "titulo": b.titulo,
        "link": b.link,
        "imagen_url": "/static/banners/" + b.imagen_url
    } for b in banners]

    # Agregamos los dos banners fijos
    banners_dict.append({
        "titulo": "🏪 ¡Patrocina tu comercio!",
        "link": "/subir-banner",
        "imagen_url": "/static/img/patrocina.png"
    })
    banners_dict.append({
        "titulo": "💰 ¡Dona para no tener publicidad!",
        "link": "https://cafecito.app/glutymap",
        "imagen_url": "/static/img/donar.png"
    })

    return dict(banners=banners_dict)





@app.route('/donar')
@login_required
def donar():
    return render_template('donar.html')

@app.route('/enviar-comprobante', methods=['POST'])
@login_required
def enviar_comprobante():
    archivo = request.files['comprobante']
    if archivo:
        msg = Message("📥 Nuevo comprobante de donación",
                      recipients=["tucorreo@gmail.com"])  # Tu correo de recepción
        msg.body = f"El usuario {current_user.email} ha subido un comprobante de donación."
        msg.attach(archivo.filename, archivo.mimetype, archivo.read())
        mail.send(msg)
        flash("✅ Comprobante enviado correctamente. ¡Gracias por tu apoyo!", "success")
    else:
        flash("❌ No se adjuntó ningún archivo.", "danger")
    return redirect(url_for('donar'))




@app.route('/recomendados')
def recomendados():
    lugares = LugarSugerido.query.filter_by(destacado=True).all()
    return render_template('recomendados.html', lugares=lugares)



@app.route('/vincular/<int:lugar_id>', methods=['GET', 'POST'])
@login_required
def vincular_lugar(lugar_id):
    if not current_user.is_admin:
        flash("Acceso denegado", "danger")
        return redirect(url_for('revisar_lugares'))

    lugar = LugarSugerido.query.get_or_404(lugar_id)
    usuarios = Usuario.query.all()

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        usuario = Usuario.query.get(usuario_id)

        if usuario:
            lugar.usuario_id = usuario.id
            db.session.commit()
            flash(f"Lugar '{lugar.nombre}' vinculado con {usuario.email}", "success")
            return redirect(url_for('revisar_lugares'))
        else:
            flash("Usuario no encontrado", "danger")

    return render_template("vincular_lugar.html", lugar=lugar, usuarios=usuarios)


@app.route('/aprobar/<int:id>', methods=['POST'])
@login_required
def aprobar_lugar(id):
    if not current_user.is_admin:
        flash("Solo los administradores pueden aprobar lugares.", "danger")
        return redirect(url_for('revisar_lugares'))

    lugar = LugarSugerido.query.get_or_404(id)
    lugar.aprobado = True
    lugar.rechazado = False

    # Si el usuario que lo sugirió es un comercio, lo vinculamos
    if lugar.usuario and lugar.usuario.es_comercio:
        lugar.usuario_id = lugar.usuario.id


    db.session.commit()

    if lugar.usuario and lugar.usuario.email:
        try:
            msg = Message("✅ ¡Tu lugar fue aprobado en GlutyMap!", recipients=[lugar.usuario.email])
            msg.body = f"""
    Hola {lugar.usuario.email} 👋

    Tu sugerencia para el lugar "{lugar.nombre}" fue aprobada y ya está visible en GlutyMap 🎉

    ¡Gracias por contribuir con la comunidad sin TACC!

    — GlutyMap Team
    """
            mail.send(msg)
        except Exception as e:
            print("❌ Error al enviar mail de aprobación:", e)


    flash(f"Lugar '{lugar.nombre}' aprobado correctamente.", "success")
    return redirect(url_for('revisar_lugares'))


@app.route('/rechazar/<int:lugar_id>', methods=['POST'])
@login_required
def rechazar_lugar(lugar_id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.get_or_404(lugar_id)
    lugar.aprobado = False
    lugar.rechazado = True
    db.session.commit()

    if lugar.usuario and lugar.usuario.email:
        try:
            msg = Message("❌ Tu sugerencia fue rechazada en GlutyMap", recipients=[lugar.usuario.email])
            msg.body = f"""
    Hola {lugar.usuario.email} 👋

    Lamentablemente, tu sugerencia para el lugar "{lugar.nombre}" no pudo ser aprobada.

    Puede que no cumpla con los criterios de la plataforma, esté duplicada o falte información clave.

    Te agradecemos igualmente por tomarte el tiempo de enviarla ❤️

    — GlutyMap Team
    """
            mail.send(msg)
        except Exception as e:
            print("❌ Error al enviar mail de rechazo:", e)


    flash('❌ Lugar rechazado.', 'danger')
    return redirect(url_for('revisar_lugares'))

def geocodificar_direccion(direccion_completa):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": direccion_completa, "format": "json", "limit": 1}
    headers = {
    "User-Agent": "GlutyMapApp/1.0 (contacto: glutymap.info@gmail.com)",
    "Referer": "https://glutymap.com"
}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            print(f"[Geocodificación exitosa] {direccion_completa} → {data[0]['lat']}, {data[0]['lon']}")
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            print(f"[Geocodificación sin resultados] {direccion_completa}")
    except Exception as e:
        print(f"[Error geocodificación] {direccion_completa} → {e}")

    return None, None

@app.route('/admin/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)

    total = LugarSugerido.query.count()
    aprobados = LugarSugerido.query.filter_by(aprobado=True, rechazado=False).count()
    pendientes = LugarSugerido.query.filter_by(aprobado=False, rechazado=False).count()
    rechazados = LugarSugerido.query.filter_by(rechazado=True).count()
    lugares = LugarSugerido.query.all()

    from collections import Counter
    from models import LogAccion
    from datetime import datetime

    # Usuarios
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    total_admins = sum(1 for u in usuarios if u.is_admin)

    # Provincias
    provincia_counter = Counter([l.provincia for l in lugares if l.provincia])
    provincias_labels = list(provincia_counter.keys())
    provincias_data = list(provincia_counter.values())

    # Últimos lugares
    ultimos_lugares = LugarSugerido.query.order_by(LugarSugerido.fecha_envio.desc()).limit(5).all()

    # Filtros logs
    accion_filtro = request.args.get('accion')
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')
    query_logs = LogAccion.query

    if accion_filtro in ['Hacer admin', 'Quitar admin']:
        query_logs = query_logs.filter_by(accion=accion_filtro)
    if fecha_desde:
        try:
            f_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query_logs = query_logs.filter(LogAccion.fecha >= f_desde)
        except ValueError:
            pass
    if fecha_hasta:
        try:
            f_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            query_logs = query_logs.filter(LogAccion.fecha <= f_hasta)
        except ValueError:
            pass

    ultimos_logs = query_logs.order_by(LogAccion.fecha.desc()).limit(10).all()

    return render_template("dashboard.html",
        total=total,
        aprobados=aprobados,
        pendientes=pendientes,
        rechazados=rechazados,
        lugares=lugares,
        total_usuarios=total_usuarios,
        total_admins=total_admins,
        provincias_labels=provincias_labels,
        provincias_data=provincias_data,
        ultimos_lugares=ultimos_lugares,
        ultimos_logs=ultimos_logs,
        accion_filtro=accion_filtro,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )



@app.route('/admin/eliminar/<int:lugar_id>', methods=['POST'])
@login_required
def eliminar_lugar(lugar_id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.get_or_404(lugar_id)
    db.session.delete(lugar)
    db.session.commit()

    flash('🗑️ Lugar eliminado correctamente.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/exportar_csv')
@login_required
def exportar_csv():
    if not current_user.is_admin:
        abort(403)

    import csv
    from io import StringIO, BytesIO
    from zipfile import ZipFile
    from collections import Counter
    from models import LugarSugerido, Usuario, LogAccion
    from datetime import datetime

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:

        # 1. Sugerencias
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Nombre", "Dirección", "Ciudad", "Provincia", "País", "Tipo", "Comentarios", "Lat", "Lng", "Estado", "Fecha envío"])
        for l in LugarSugerido.query.all():
            estado = "Aprobado" if l.aprobado else "Rechazado" if l.rechazado else "Pendiente"
            writer.writerow([l.nombre, l.direccion, l.ciudad, l.provincia, l.pais, l.tipo, l.comentarios, l.lat, l.lng, estado, l.fecha_envio])
        zf.writestr("sugerencias.csv", buffer.getvalue())

        # 2. Usuarios
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Email", "Es admin"])
        for u in Usuario.query.all():
            writer.writerow([u.email, "Sí" if u.is_admin else "No"])
        zf.writestr("usuarios.csv", buffer.getvalue())

        # 3. Logs
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Fecha", "Admin", "Usuario Afectado", "Acción"])
        for log in LogAccion.query.order_by(LogAccion.fecha.desc()).all():
            writer.writerow([
                log.fecha.strftime('%Y-%m-%d %H:%M'),
                log.admin.email,
                log.usuario_afectado.email,
                log.accion
            ])
        zf.writestr("logs_acciones.csv", buffer.getvalue())

        # 4. Últimos lugares
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Nombre", "Provincia", "Fecha"])
        for l in LugarSugerido.query.order_by(LugarSugerido.fecha_envio.desc()).limit(10).all():
            writer.writerow([l.nombre, l.provincia, l.fecha_envio])
        zf.writestr("ultimos_lugares.csv", buffer.getvalue())

        # 5. Sugerencias por provincia
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Provincia", "Cantidad"])
        contador = Counter([l.provincia for l in LugarSugerido.query.all() if l.provincia])
        for prov, cant in contador.items():
            writer.writerow([prov, cant])
        zf.writestr("sugerencias_por_provincia.csv", buffer.getvalue())

    memory_file.seek(0)
    fecha_hoy = datetime.today().strftime("%Y-%m-%d")
    return Response(
        memory_file.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment;filename=informe_completo_{fecha_hoy}.zip'}
    )


@app.route('/admin/editar_ubicacion/<int:lugar_id>', methods=['GET', 'POST'])
@login_required
def editar_ubicacion(lugar_id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.get_or_404(lugar_id)

    # ✅ Limpieza explícita
    if lugar.lat in ("NULL", "", None):
        lugar.lat = None
    if lugar.lng in ("NULL", "", None):
        lugar.lng = None

    if request.method == 'POST':
        lugar.lat = float(request.form['lat'])
        lugar.lng = float(request.form['lng'])
        db.session.commit()
        flash('✅ Ubicación actualizada correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('editar_ubicacion.html', lugar=lugar)

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 8  # usuarios por página

    usuarios = Usuario.query.order_by(Usuario.email).paginate(page=page, per_page=per_page)

    return render_template("admin_usuarios.html", usuarios=usuarios)


@app.route('/admin/usuarios/toggle_admin/<int:id>')
@login_required
def toggle_admin(id):
    if not current_user.is_admin:
        abort(403)

    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        login_user(usuario)  # 👈 Esto actualiza current_user en la sesión
        flash("No podés cambiar tu propio permiso de admin.", "warning")
        return redirect(url_for('admin_usuarios'))

    # 👉 Primero invertimos el estado
    usuario.is_admin = not usuario.is_admin

    # 👉 Luego registramos correctamente la acción
    from models import LogAccion
    accion = "Hacer admin" if usuario.is_admin else "Quitar admin"
    nuevo_log = LogAccion(
        admin_id=current_user.id,
        usuario_afectado_id=usuario.id,
        accion=accion
    )
    db.session.add(nuevo_log)

    db.session.commit()

    flash(f"Permisos actualizados para {usuario.email}.", "success")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/toggle_publicidad/<int:id>')
@login_required
def toggle_publicidad(id):
    if not current_user.is_admin:
        abort(403)

    usuario = Usuario.query.get_or_404(id)
    usuario.publicidad_activa = not usuario.publicidad_activa
    db.session.commit()

    estado = "activada" if usuario.publicidad_activa else "desactivada"
    flash(f"Publicidad {estado} para {usuario.email}.", "info")
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/desvincular_comercio/<int:id>', methods=['POST'])
@login_required
def desvincular_comercio(id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.filter_by(usuario_id=id).first()
    if lugar:
        lugar.usuario_id = None
        db.session.commit()
        flash(f"Comercio desvinculado de {lugar.nombre}.", "info")
    else:
        flash("Este usuario no tiene comercio vinculado.", "warning")

    return redirect(url_for('admin_usuarios'))


#@app.route("/init_db")
#def init_db():
    #from app import db
    #db.create_all()
    #return "✅ Tablas creadas en Neon"


@app.route('/ads.txt')
def ads_txt():
    return Response(
        "google.com, pub-6411447824601126, DIRECT, f08c47fec0942fa0",
        mimetype='text/plain'
    )

@app.route("/privacidad")
def politica_privacidad():
    return render_template("privacidad.html")

@app.route("/terminos")
def terminos_condiciones():
    return render_template("terminos.html")

@app.route("/cookies")
def politica_cookies():
    return render_template("cookies.html")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


# ============================================================================
# NUEVAS RUTAS PARA LOCALHUB - SISTEMA DE MENÚS Y CRM MEJORADO
# ============================================================================

# ------------ RUTAS PARA GESTIÓN DE MENÚS ------------

@app.route('/mi-comercio/menus')
@login_required
def gestionar_menus():
    """Dashboard de gestión de menús del comercio"""
    if not current_user.es_comercio:
        flash('Debes tener una cuenta de comercio para acceder', 'error')
        return redirect(url_for('ver_mapa'))

    # Obtener el lugar asociado
    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        flash('Tu comercio aún no ha sido aprobado', 'warning')
        return redirect(url_for('mi_comercio'))

    menus = Menu.query.filter_by(lugar_id=lugar[0].id).order_by(Menu.orden).all()
    return render_template('gestionar_menus.html', lugar=lugar[0], menus=menus)


@app.route('/mi-comercio/menus/crear', methods=['GET', 'POST'])
@login_required
def crear_menu():
    """Crear un nuevo menú"""
    if not current_user.es_comercio:
        abort(403)

    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        abort(403)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        archivo = request.files.get('archivo')

        if not nombre:
            flash('El nombre del menú es obligatorio', 'error')
            return redirect(url_for('crear_menu'))

        # Crear menú
        menu = Menu(
            lugar_id=lugar[0].id,
            nombre=nombre,
            descripcion=descripcion,
            orden=Menu.query.filter_by(lugar_id=lugar[0].id).count()
        )

        # Subir archivo si existe
        if archivo and archivo.filename:
            try:
                archivo_url = utils.save_uploaded_file(archivo, 'menus', f'menu_{lugar[0].id}')
                menu.archivo_url = archivo_url
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('crear_menu'))

        db.session.add(menu)
        db.session.commit()

        flash('Menú creado exitosamente', 'success')
        return redirect(url_for('gestionar_menus'))

    return render_template('crear_menu.html', lugar=lugar[0])


@app.route('/mi-comercio/menus/<int:menu_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_menu(menu_id):
    """Editar un menú existente"""
    menu = Menu.query.get_or_404(menu_id)

    # Verificar que el menú pertenece al comercio del usuario
    lugar = current_user.lugar_asociado
    if not lugar or menu.lugar_id != lugar[0].id:
        abort(403)

    if request.method == 'POST':
        menu.nombre = request.form.get('nombre', menu.nombre)
        menu.descripcion = request.form.get('descripcion', '')
        menu.activo = request.form.get('activo') == 'on'

        # Actualizar archivo si se sube uno nuevo
        archivo = request.files.get('archivo')
        if archivo and archivo.filename:
            try:
                archivo_url = utils.save_uploaded_file(archivo, 'menus', f'menu_{lugar[0].id}')
                menu.archivo_url = archivo_url
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('editar_menu', menu_id=menu_id))

        menu.fecha_actualizacion = datetime.utcnow()
        db.session.commit()

        flash('Menú actualizado exitosamente', 'success')
        return redirect(url_for('gestionar_menus'))

    return render_template('editar_menu.html', menu=menu, lugar=lugar[0])


@app.route('/mi-comercio/menus/<int:menu_id>/eliminar', methods=['POST'])
@login_required
def eliminar_menu(menu_id):
    """Eliminar un menú"""
    menu = Menu.query.get_or_404(menu_id)

    lugar = current_user.lugar_asociado
    if not lugar or menu.lugar_id != lugar[0].id:
        abort(403)

    db.session.delete(menu)
    db.session.commit()

    flash('Menú eliminado exitosamente', 'success')
    return redirect(url_for('gestionar_menus'))


@app.route('/mi-comercio/menus/<int:menu_id>/items', methods=['GET', 'POST'])
@login_required
def gestionar_items_menu(menu_id):
    """Gestionar items de un menú"""
    menu = Menu.query.get_or_404(menu_id)

    lugar = current_user.lugar_asociado
    if not lugar or menu.lugar_id != lugar[0].id:
        abort(403)

    if request.method == 'POST':
        # Agregar nuevo item
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = request.form.get('precio')
        categoria_item = request.form.get('categoria_item', '')

        if not nombre:
            flash('El nombre del item es obligatorio', 'error')
            return redirect(url_for('gestionar_items_menu', menu_id=menu_id))

        item = ItemMenu(
            menu_id=menu.id,
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio) if precio else None,
            categoria_item=categoria_item,
            orden=ItemMenu.query.filter_by(menu_id=menu.id).count()
        )

        db.session.add(item)
        db.session.commit()

        flash('Item agregado exitosamente', 'success')
        return redirect(url_for('gestionar_items_menu', menu_id=menu_id))

    items = ItemMenu.query.filter_by(menu_id=menu.id).order_by(ItemMenu.orden).all()
    return render_template('gestionar_items.html', menu=menu, items=items, lugar=lugar[0])


@app.route('/mi-comercio/items/<int:item_id>/eliminar', methods=['POST'])
@login_required
def eliminar_item(item_id):
    """Eliminar un item del menú"""
    item = ItemMenu.query.get_or_404(item_id)
    menu_id = item.menu_id

    menu = Menu.query.get(menu_id)
    lugar = current_user.lugar_asociado
    if not lugar or menu.lugar_id != lugar[0].id:
        abort(403)

    db.session.delete(item)
    db.session.commit()

    flash('Item eliminado exitosamente', 'success')
    return redirect(url_for('gestionar_items_menu', menu_id=menu_id))


# ------------ RUTAS PARA GESTIÓN DE REDES SOCIALES Y QR ------------

@app.route('/mi-comercio/redes-sociales', methods=['GET', 'POST'])
@login_required
def gestionar_redes_sociales():
    """Gestionar redes sociales y generar QR codes"""
    if not current_user.es_comercio:
        abort(403)

    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        abort(403)

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        url_perfil = request.form.get('url_perfil')

        if not tipo or not url_perfil:
            flash('Tipo y URL son obligatorios', 'error')
            return redirect(url_for('gestionar_redes_sociales'))

        # Generar QR code
        qr_code_url = utils.generate_social_qr(lugar[0].id, tipo, url_perfil)

        red_social = RedSocial(
            lugar_id=lugar[0].id,
            tipo=tipo,
            url_perfil=url_perfil,
            qr_code_url=qr_code_url
        )

        db.session.add(red_social)
        db.session.commit()

        flash('Red social agregada y QR generado exitosamente', 'success')
        return redirect(url_for('gestionar_redes_sociales'))

    redes = RedSocial.query.filter_by(lugar_id=lugar[0].id).all()
    return render_template('gestionar_redes.html', lugar=lugar[0], redes=redes)


@app.route('/mi-comercio/redes-sociales/<int:red_id>/eliminar', methods=['POST'])
@login_required
def eliminar_red_social(red_id):
    """Eliminar una red social"""
    red = RedSocial.query.get_or_404(red_id)

    lugar = current_user.lugar_asociado
    if not lugar or red.lugar_id != lugar[0].id:
        abort(403)

    db.session.delete(red)
    db.session.commit()

    flash('Red social eliminada exitosamente', 'success')
    return redirect(url_for('gestionar_redes_sociales'))


@app.route('/mi-comercio/qr-tarjeta')
@login_required
def generar_qr_tarjeta():
    """Generar QR code con info completa del comercio"""
    if not current_user.es_comercio:
        abort(403)

    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        abort(403)

    qr_url = utils.generate_business_card_qr(lugar[0])

    return render_template('qr_tarjeta.html', lugar=lugar[0], qr_url=qr_url)


# ------------ RUTAS PARA GESTIÓN DE FOTOS ------------

@app.route('/mi-comercio/fotos', methods=['GET', 'POST'])
@login_required
def gestionar_fotos():
    """Gestionar galería de fotos del comercio"""
    if not current_user.es_comercio:
        abort(403)

    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        abort(403)

    if request.method == 'POST':
        foto = request.files.get('foto')
        descripcion = request.form.get('descripcion', '')
        es_principal = request.form.get('es_principal') == 'on'

        if foto and foto.filename:
            try:
                foto_url = utils.save_uploaded_file(foto, 'fotos', f'lugar_{lugar[0].id}')

                # Si es foto principal, desmarcar las demás
                if es_principal:
                    FotoLugar.query.filter_by(lugar_id=lugar[0].id, es_principal=True).update({'es_principal': False})

                nueva_foto = FotoLugar(
                    lugar_id=lugar[0].id,
                    url=foto_url,
                    descripcion=descripcion,
                    es_principal=es_principal,
                    orden=FotoLugar.query.filter_by(lugar_id=lugar[0].id).count()
                )

                db.session.add(nueva_foto)
                db.session.commit()

                flash('Foto subida exitosamente', 'success')
            except ValueError as e:
                flash(str(e), 'error')

        return redirect(url_for('gestionar_fotos'))

    fotos = FotoLugar.query.filter_by(lugar_id=lugar[0].id).order_by(FotoLugar.orden).all()
    return render_template('gestionar_fotos.html', lugar=lugar[0], fotos=fotos)


@app.route('/mi-comercio/fotos/<int:foto_id>/eliminar', methods=['POST'])
@login_required
def eliminar_foto(foto_id):
    """Eliminar una foto"""
    foto = FotoLugar.query.get_or_404(foto_id)

    lugar = current_user.lugar_asociado
    if not lugar or foto.lugar_id != lugar[0].id:
        abort(403)

    db.session.delete(foto)
    db.session.commit()

    flash('Foto eliminada exitosamente', 'success')
    return redirect(url_for('gestionar_fotos'))


# ------------ ACTUALIZACIÓN DE VISTA DE COMERCIO ------------

@app.route('/mi-comercio/actualizar-info', methods=['POST'])
@login_required
def actualizar_info_comercio():
    """Actualizar información básica del comercio"""
    if not current_user.es_comercio:
        abort(403)

    lugar = current_user.lugar_asociado
    if not lugar or not lugar[0].aprobado:
        abort(403)

    lugar_obj = lugar[0]

    # Actualizar campos
    lugar_obj.descripcion = request.form.get('descripcion', '')
    lugar_obj.telefono = request.form.get('telefono', '')
    lugar_obj.email_contacto = request.form.get('email_contacto', '')
    lugar_obj.sitio_web = request.form.get('sitio_web', '')

    # Actualizar horarios (JSON)
    horarios = {}
    for dia in ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']:
        apertura = request.form.get(f'{dia}_apertura')
        cierre = request.form.get(f'{dia}_cierre')
        if apertura and cierre:
            horarios[dia] = {'apertura': apertura, 'cierre': cierre}

    lugar_obj.horarios = utils.format_horarios(horarios)

    db.session.commit()

    flash('Información actualizada exitosamente', 'success')
    return redirect(url_for('mi_comercio'))


# ------------ RUTA MEJORADA DE MI COMERCIO ------------

@app.route('/mi-comercio/dashboard')
@login_required
def mi_comercio_dashboard():
    """Dashboard completo del comercio con todas las opciones"""
    if not current_user.es_comercio:
        flash('Necesitas una cuenta de comercio', 'error')
        return redirect(url_for('ver_mapa'))

    lugar = current_user.lugar_asociado
    if not lugar:
        flash('Aún no tienes un comercio vinculado', 'warning')
        return redirect(url_for('ver_mapa'))

    lugar_obj = lugar[0]

    # Obtener estadísticas
    total_menus = Menu.query.filter_by(lugar_id=lugar_obj.id).count()
    total_fotos = FotoLugar.query.filter_by(lugar_id=lugar_obj.id).count()
    total_redes = RedSocial.query.filter_by(lugar_id=lugar_obj.id).count()
    total_reviews = Review.query.filter_by(lugar_id=lugar_obj.id).count()

    # Calcular promedio de reviews
    avg_rating = db.session.query(func.avg(Review.puntuacion)).filter(
        Review.lugar_id == lugar_obj.id
    ).scalar() or 0

    return render_template('mi_comercio_dashboard.html',
                         lugar=lugar_obj,
                         total_menus=total_menus,
                         total_fotos=total_fotos,
                         total_redes=total_redes,
                         total_reviews=total_reviews,
                         avg_rating=round(avg_rating, 1))


# ------------ OBTENER CATEGORÍAS Y ETIQUETAS (API) ------------

@app.route('/api/categorias')
def api_categorias():
    """Obtener todas las categorías activas"""
    categorias = Categoria.query.filter_by(activo=True).order_by(Categoria.orden).all()
    return {
        'categorias': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'slug': c.slug,
                'icono': c.icono,
                'color': c.color
            } for c in categorias
        ]
    }


@app.route('/api/etiquetas')
def api_etiquetas():
    """Obtener todas las etiquetas activas"""
    etiquetas = EtiquetaEspecial.query.filter_by(activo=True).all()
    return {
        'etiquetas': [
            {
                'id': e.id,
                'nombre': e.nombre,
                'slug': e.slug,
                'icono': e.icono,
                'color': e.color
            } for e in etiquetas
        ]
    }


if __name__ == '__main__':
    app.run(debug=True)