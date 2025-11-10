-- ============================================
-- MIGRACIÓN LOCALHUB - SQL DIRECTO
-- Ejecutar en Neon o consola PostgreSQL
-- ============================================

-- 1. CREAR TABLA DE CATEGORÍAS
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    icono VARCHAR(50),
    color VARCHAR(7) DEFAULT '#3388ff',
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    orden INTEGER DEFAULT 0
);

-- 2. CREAR TABLA DE ETIQUETAS ESPECIALES
CREATE TABLE IF NOT EXISTS etiquetas_especiales (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    icono VARCHAR(50),
    color VARCHAR(7) DEFAULT '#28a745',
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    orden INTEGER DEFAULT 0
);

-- 3. CREAR TABLA DE RELACIÓN LUGAR-CATEGORÍAS (many-to-many)
CREATE TABLE IF NOT EXISTS lugar_categorias (
    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
    PRIMARY KEY (lugar_id, categoria_id)
);

-- 4. CREAR TABLA DE RELACIÓN LUGAR-ETIQUETAS (many-to-many)
CREATE TABLE IF NOT EXISTS lugar_etiquetas (
    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
    etiqueta_id INTEGER NOT NULL REFERENCES etiquetas_especiales(id) ON DELETE CASCADE,
    PRIMARY KEY (lugar_id, etiqueta_id)
);

-- 5. CREAR TABLA DE MENÚS
CREATE TABLE IF NOT EXISTS menus (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    archivo_url VARCHAR(300),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. CREAR TABLA DE ITEMS DE MENÚ
CREATE TABLE IF NOT EXISTS items_menu (
    id SERIAL PRIMARY KEY,
    menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(50),
    disponible BOOLEAN DEFAULT TRUE,
    orden INTEGER DEFAULT 0
);

-- 7. CREAR TABLA DE REDES SOCIALES
CREATE TABLE IF NOT EXISTS redes_sociales (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    url_perfil VARCHAR(300) NOT NULL,
    qr_code_url VARCHAR(300),
    clics INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. CREAR TABLA DE FOTOS
CREATE TABLE IF NOT EXISTS fotos_lugar (
    id SERIAL PRIMARY KEY,
    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
    url VARCHAR(300) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. AGREGAR NUEVAS COLUMNAS A lugar_sugerido
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS email_contacto VARCHAR(150);
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS sitio_web VARCHAR(200);
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS vistas INTEGER DEFAULT 0;
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS clics_como_llegar INTEGER DEFAULT 0;
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS clics_telefono INTEGER DEFAULT 0;
ALTER TABLE lugar_sugerido ADD COLUMN IF NOT EXISTS horarios TEXT;

-- 10. CREAR ÍNDICES PARA MEJOR RENDIMIENTO
CREATE INDEX IF NOT EXISTS idx_lugar_categorias_lugar ON lugar_categorias(lugar_id);
CREATE INDEX IF NOT EXISTS idx_lugar_categorias_categoria ON lugar_categorias(categoria_id);
CREATE INDEX IF NOT EXISTS idx_lugar_etiquetas_lugar ON lugar_etiquetas(lugar_id);
CREATE INDEX IF NOT EXISTS idx_lugar_etiquetas_etiqueta ON lugar_etiquetas(etiqueta_id);
CREATE INDEX IF NOT EXISTS idx_menus_lugar ON menus(lugar_id);
CREATE INDEX IF NOT EXISTS idx_items_menu_menu ON items_menu(menu_id);
CREATE INDEX IF NOT EXISTS idx_redes_sociales_lugar ON redes_sociales(lugar_id);
CREATE INDEX IF NOT EXISTS idx_fotos_lugar_lugar ON fotos_lugar(lugar_id);

-- ============================================
-- MIGRACIÓN COMPLETADA
-- ============================================
-- Ahora ejecuta: python3 init_categories.py
-- Para poblar las categorías y etiquetas iniciales
-- ============================================
