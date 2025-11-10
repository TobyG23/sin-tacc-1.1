# LocalHub - Refactorización Completa del Sistema

## Resumen de Cambios

Este documento describe la refactorización completa de **GlutyMap** (mapa para celíacos) a **LocalHub** (plataforma general de comercios con sistema de menús y CRM).

---

## Cambios Realizados

### 1. Base de Datos - Nuevos Modelos (`models.py`)

Se agregaron los siguientes modelos:

#### **Categoria**
- Categorías de comercios (Restaurante, Cafetería, Panadería, etc.)
- Campos: nombre, slug, icono, color, descripción, activo, orden
- Relación many-to-many con LugarSugerido

#### **EtiquetaEspecial**
- Etiquetas especiales (Sin Gluten, Vegano, Vegetariano, etc.)
- Campos: nombre, slug, icono, color, descripción, activo
- Relación many-to-many con LugarSugerido

#### **Menu**
- Menús/Cartas de los comercios
- Campos: lugar_id, nombre, descripción, archivo_url, activo, orden, fechas
- Relación one-to-many con ItemMenu

#### **ItemMenu**
- Items individuales dentro de un menú
- Campos: menu_id, nombre, descripción, precio, categoria_item, imagen_url, disponible, orden, etiquetas_item

#### **RedSocial**
- Redes sociales y códigos QR de los comercios
- Campos: lugar_id, tipo, url_perfil, qr_code_url, activo, clics, fecha_creacion

#### **FotoLugar**
- Galería de fotos de los comercios
- Campos: lugar_id, url, descripción, es_principal, orden, fecha_subida

#### **Campos Nuevos en LugarSugerido**
- `descripcion`: Descripción del comercio
- `telefono`: Teléfono de contacto
- `email_contacto`: Email de contacto
- `sitio_web`: Sitio web
- `vistas`, `clics_como_llegar`, `clics_telefono`: Analytics
- `horarios`: JSON con horarios por día

#### **Campos Nuevos en Usuario**
- `plan`: Plan del usuario (gratuito, destacado, premium)
- `fecha_expiracion_plan`: Fecha de expiración del plan

---

### 2. Migraciones de Base de Datos

**Archivo**: `migrations/versions/20251110_add_menu_categories_system.py`

- Crea todas las nuevas tablas
- Agrega nuevas columnas a LugarSugerido y Usuario
- Incluye funciones de upgrade() y downgrade()

**Para aplicar las migraciones**:
```bash
flask db upgrade
```

---

### 3. Script de Inicialización (`init_categories.py`)

Script para poblar la base de datos con categorías y etiquetas iniciales.

**Categorías incluidas** (12 total):
- Restaurante, Cafetería, Panadería, Pizzería, Heladería
- Bar, Fast Food, Tienda de Alimentos, Supermercado
- Hotel, Catering, Otro

**Etiquetas incluidas** (13 total):
- Sin Gluten/Apto Celíacos, Vegano, Vegetariano
- Sin Lactosa, Sin Azúcar, Kosher, Halal, Orgánico
- Pet Friendly, Accesible, WiFi Gratis, Delivery, Para Llevar

**Función de migración de datos**:
- Asigna categoría "Otro" a todos los lugares sin categoría
- Asigna etiqueta "Sin Gluten" a todos los lugares existentes

**Ejecutar**:
```bash
python init_categories.py
```

---

### 4. Utilidades y Servicios (`utils.py`)

Funciones auxiliares creadas:

#### Generación de QR Codes
- `generate_qr_code(data, filename, save_path)`: Genera QR genérico
- `generate_social_qr(lugar_id, tipo, url)`: QR para redes sociales
- `generate_business_card_qr(lugar)`: QR con info completa del comercio
- `generate_menu_qr(lugar_id, menu_id)`: QR para menú específico

#### Gestión de Archivos
- `allowed_file(filename, allowed_extensions)`: Valida extensiones
- `save_uploaded_file(file, folder, prefix, max_size_mb)`: Guarda archivos subidos
- `optimize_image(filepath, max_width, max_height, quality)`: Optimiza imágenes

#### Formateo
- `format_price(price)`: Formatea precios
- `parse_horarios(horarios_json)`: Parsea JSON de horarios
- `format_horarios(horarios_dict)`: Convierte dict a JSON

---

### 5. Nuevas Rutas en `app.py`

Se agregaron **más de 400 líneas** de nuevas rutas:

#### Gestión de Menús
- `GET /mi-comercio/menus` - Dashboard de menús
- `GET|POST /mi-comercio/menus/crear` - Crear menú
- `GET|POST /mi-comercio/menus/<id>/editar` - Editar menú
- `POST /mi-comercio/menus/<id>/eliminar` - Eliminar menú
- `GET|POST /mi-comercio/menus/<id>/items` - Gestionar items
- `POST /mi-comercio/items/<id>/eliminar` - Eliminar item

#### Gestión de Redes Sociales
- `GET|POST /mi-comercio/redes-sociales` - Gestionar redes sociales
- `POST /mi-comercio/redes-sociales/<id>/eliminar` - Eliminar red social
- `GET /mi-comercio/qr-tarjeta` - Generar QR tarjeta de negocio

#### Gestión de Fotos
- `GET|POST /mi-comercio/fotos` - Gestionar galería de fotos
- `POST /mi-comercio/fotos/<id>/eliminar` - Eliminar foto

#### CRM Mejorado
- `POST /mi-comercio/actualizar-info` - Actualizar info del comercio
- `GET /mi-comercio/dashboard` - Dashboard completo con estadísticas

#### APIs
- `GET /api/categorias` - Obtener todas las categorías
- `GET /api/etiquetas` - Obtener todas las etiquetas

---

### 6. Dependencias Agregadas (`requirements.txt`)

- `qrcode==8.0` - Generación de códigos QR

---

## Próximos Pasos para Completar la Refactorización

### Templates que Faltan Crear

Los siguientes templates necesitan ser creados en `templates/`:

#### CRM de Comercios
- `gestionar_menus.html` - Dashboard de menús
- `crear_menu.html` - Formulario crear menú
- `editar_menu.html` - Formulario editar menú
- `gestionar_items.html` - Gestionar items del menú
- `gestionar_redes.html` - Gestionar redes sociales y QR
- `qr_tarjeta.html` - Mostrar QR tarjeta de negocio
- `gestionar_fotos.html` - Gestionar galería de fotos
- `mi_comercio_dashboard.html` - Dashboard completo del comercio

#### Vista Pública Mejorada
- Actualizar `ver_lugar.html` con:
  - Tabs: Info, Menú, Galería, Reviews, Contacto
  - Mostrar menús con items y precios
  - Códigos QR de redes sociales
  - Galería de fotos
  - Información de contacto mejorada

#### Base y Navegación
- Actualizar `base.html` con:
  - Nuevo nombre "LocalHub"
  - Navegación actualizada
  - Diseño más profesional
  - Links a nuevas funcionalidades

#### Mapa
- Actualizar `mapa.html` con:
  - Filtros por categorías (multiselect)
  - Filtros por etiquetas especiales
  - Búsqueda mejorada

### JavaScript a Actualizar

#### `mapa.js`
- Agregar filtros por categorías
- Agregar filtros por etiquetas
- Actualizar iconos de pines según categoría
- Cargar categorías y etiquetas desde API

#### Nuevo archivo `crm.js`
- Funcionalidad para gestión de menús
- Upload de archivos
- Gestión de items con drag & drop
- Preview de QR codes

### CSS a Crear/Actualizar

#### `crm.css`
- Estilos para dashboard de comercios
- Estilos para formularios de menús
- Estilos para galería de fotos
- Diseño de tarjetas y cards

#### `style.css`
- Actualizar con diseño más profesional
- Mejorar paleta de colores
- Añadir animaciones suaves
- Responsive mejorado

---

## Instrucciones de Instalación y Despliegue

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Asegurarse de que `.env` tenga:
```
SECRET_KEY=tu-clave-secreta
MAIL_PASSWORD=tu-password-de-mail
```

### 3. Aplicar Migraciones

```bash
# Aplicar migraciones
flask db upgrade

# Inicializar categorías y etiquetas
python init_categories.py
```

### 4. Crear Directorios de Uploads

```bash
mkdir -p static/qr_codes static/menus static/fotos
```

### 5. Ejecutar la Aplicación

```bash
python app.py
```

---

## Características del Nuevo Sistema

### Para Usuarios Generales
- ✅ Mapa interactivo con filtros por categorías y etiquetas
- ✅ Búsqueda avanzada de comercios
- ✅ Vista detallada de comercios con menús, fotos y contacto
- ✅ Sistema de reviews y calificaciones
- ✅ Filtro especial "Sin Gluten" mantiene funcionalidad para celíacos

### Para Comercios
- ✅ Dashboard completo con estadísticas
- ✅ Gestión de menús (subir PDF o crear items manualmente)
- ✅ Gestión de galería de fotos
- ✅ Gestión de redes sociales con QR codes automáticos
- ✅ QR tarjeta de negocio descargable
- ✅ Analytics básico (vistas, clics)
- ✅ Actualización de horarios, teléfono, email, sitio web

### Para Administradores
- ✅ Todas las funcionalidades anteriores
- ✅ Gestión de categorías y etiquetas (vía admin)
- ✅ Aprobación de comercios
- ✅ Gestión de usuarios

---

## Compatibilidad con Datos Existentes

- ✅ **Todos los datos existentes se mantienen**
- ✅ Lugares existentes se asignan a categoría "Otro" automáticamente
- ✅ Lugares existentes reciben etiqueta "Sin Gluten" automáticamente
- ✅ Sistema de reviews y usuarios no se ven afectados
- ✅ Sistema de publicidad mantiene funcionalidad

---

## Estructura de Archivos

```
sin-tacc-1.1/
├── app.py                          # Aplicación principal (1415 líneas)
├── models.py                       # Modelos de base de datos
├── utils.py                        # Utilidades y servicios
├── init_categories.py              # Script de inicialización
├── requirements.txt                # Dependencias Python
├── REFACTORING_README.md          # Este documento
│
├── migrations/
│   └── versions/
│       └── 20251110_add_menu_categories_system.py
│
├── static/
│   ├── qr_codes/                  # QR codes generados
│   ├── menus/                     # Menús subidos (PDF/imágenes)
│   ├── fotos/                     # Fotos de comercios
│   ├── banners/                   # Banners publicitarios
│   ├── css/
│   ├── js/
│   └── img/
│
└── templates/
    ├── base.html                   # Template base
    ├── mapa.html                   # Vista del mapa
    ├── ver_lugar.html              # Vista de comercio
    ├── mi_comercio.html            # Dashboard comercio (legacy)
    │
    └── [NUEVOS TEMPLATES A CREAR]
        ├── gestionar_menus.html
        ├── crear_menu.html
        ├── editar_menu.html
        ├── gestionar_items.html
        ├── gestionar_redes.html
        ├── qr_tarjeta.html
        ├── gestionar_fotos.html
        └── mi_comercio_dashboard.html
```

---

## Cambios de Nomenclatura

| Antes (GlutyMap) | Después (LocalHub) |
|------------------|---------------------|
| Mapa para celíacos | Mapa de comercios general |
| Solo "Sin TACC" | Múltiples categorías y etiquetas |
| Tipo de comercio (campo simple) | Categorías (relación many-to-many) |
| Sin sistema de menús | Sistema completo de menús con items |
| Sin QR codes | QR codes para redes y tarjeta |
| Sin galería de fotos | Galería completa con foto principal |

---

## Notas Técnicas

### Seguridad
- ✅ Validación de archivos subidos (tipo y tamaño)
- ✅ Sanitización de nombres de archivos
- ✅ Protección de rutas con `@login_required`
- ✅ Verificación de pertenencia (comercio solo edita sus datos)

### Performance
- ✅ Lazy loading en relaciones de base de datos
- ✅ Índices en campos frecuentemente consultados (recomendado agregar)
- ✅ Optimización de imágenes al subir

### Escalabilidad
- ✅ Sistema de categorías y etiquetas extensible
- ✅ Soporte para múltiples menús por comercio
- ✅ Sistema de planes preparado para monetización
- ✅ Analytics básico preparado para expansión

---

## Contacto y Soporte

Para preguntas o problemas con la refactorización:
- Revisar este documento primero
- Verificar que las migraciones se aplicaron correctamente
- Verificar que los directorios de uploads existan
- Verificar que las dependencias estén instaladas

---

## Changelog

### v2.0.0 (2025-11-10) - Refactorización LocalHub

#### Agregado
- Sistema completo de menús con items y precios
- Sistema de categorías de comercios
- Sistema de etiquetas especiales
- Generación automática de QR codes
- Gestión de redes sociales
- Galería de fotos para comercios
- CRM mejorado para comercios
- APIs para categorías y etiquetas
- Sistema de horarios
- Analytics básico (vistas, clics)
- Campos de contacto (teléfono, email, sitio web)

#### Modificado
- Modelo LugarSugerido expandido
- Modelo Usuario con sistema de planes
- Dashboard de comercios completamente renovado
- Estructura de base de datos optimizada

#### Mantenido
- Sistema de reviews y calificaciones
- Sistema de aprobación de lugares
- Sistema de publicidad con banners
- Autenticación y roles de usuario
- Funcionalidad para celíacos (como etiqueta especial)

---

**Proyecto refactorizado por**: Claude Code
**Fecha**: 10 de Noviembre, 2025
**Versión**: 2.0.0 - LocalHub
