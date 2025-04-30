import requests
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, flash, abort, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from models import db, LugarSugerido, Usuario, LogAccion


app = Flask(__name__)
app.secret_key = 'gokuesdios123'  # 🔥 Cambiar para producción

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_NdKPSa7rQ1et@ep-snowy-thunder-a4gsx6gn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def ver_mapa():
    lugares = LugarSugerido.query.filter_by(aprobado=True).all()
    return render_template('mapa.html', lugares=[l.to_dict() for l in lugares])

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

        # Validación básica de campos
        errores = []

        #Modo manual
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
        # Comentarios (opcional, pero limitamos el largo)
        if comentarios and len(comentarios) > 500:
            errores.append("El comentario es demasiado largo (máx. 500 caracteres).")
        if comentarios_mapa and len(comentarios_mapa) > 500:
            errores.append("El comentario del mapa es demasiado largo (máx. 500 caracteres).")

        # Si hay errores, los mostramos
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

        
        return redirect(url_for('ver_mapa', enviado='ok'))

    return render_template('formulario.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if Usuario.query.filter_by(email=email).first():
            flash('❌ El correo ya está registrado.', 'danger')
            return redirect(url_for('register'))

        hash = generate_password_hash(password)
        nuevo_usuario = Usuario(email=email, password=hash)
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

@app.route('/revisar')
@login_required
def revisar_lugares():
    if not current_user.is_admin:
        abort(403)

    estado = request.args.get('estado')
    page = request.args.get('page', 1, type=int)
    per_page = 6  # podés cambiar la cantidad por página

    query = LugarSugerido.query

    if estado == 'pendiente':
        query = query.filter_by(aprobado=False, rechazado=False)
    elif estado == 'aprobado':
        query = query.filter_by(aprobado=True, rechazado=False)
    elif estado == 'rechazado':
        query = query.filter_by(rechazado=True)

    lugares = query.order_by(LugarSugerido.fecha_envio.desc()).paginate(page=page, per_page=per_page)

    return render_template('revisar.html', lugares=lugares)




@app.route('/aprobar/<int:lugar_id>', methods=['POST'])
@login_required
def aprobar_lugar(lugar_id):
    if not current_user.is_admin:
        abort(403)

    lugar = LugarSugerido.query.get_or_404(lugar_id)

    if lugar.lat is None or lugar.lng is None:
        # Si no tiene coordenadas, intentamos geocodificar
        direccion_completa = f"{lugar.direccion}, {lugar.ciudad}, {lugar.provincia}, {lugar.pais}"
        lat, lng = geocodificar_direccion(direccion_completa)
        if lat and lng:
            lugar.lat = lat
            lugar.lng = lng
        else:
            flash('⚠️ No se pudo geolocalizar la dirección automáticamente.', 'warning')

    lugar.aprobado = True
    lugar.rechazado = False
    db.session.commit()

    flash('✅ Lugar aprobado correctamente.', 'success')
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

    flash('❌ Lugar rechazado.', 'danger')
    return redirect(url_for('revisar_lugares'))

def geocodificar_direccion(direccion_completa):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": direccion_completa, "format": "json", "limit": 1}
    headers = {"User-Agent": "MapaSinTACC/1.0 (tucorreo@example.com)"}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
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


@app.route("/init_db")
def init_db():
    from app import db
    db.create_all()
    return "✅ Tablas creadas en Neon"




if __name__ == '__main__':
    app.run(debug=True)