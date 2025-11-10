#!/usr/bin/env python3
"""
Script para aplicar la migración de LocalHub manualmente.
Ejecutar en el servidor de producción con: python3 apply_migration.py
"""

from app import app, db
import sys

def apply_migration():
    """Aplica las nuevas columnas y tablas a la base de datos."""

    print("=" * 60)
    print("APLICANDO MIGRACIÓN DE LOCALHUB")
    print("=" * 60)

    try:
        with app.app_context():
            # Verificar conexión
            db.session.execute(db.text('SELECT 1'))
            print("✓ Conexión a base de datos exitosa")

            # Ejecutar SQL de migración
            print("\n1. Agregando nuevas tablas...")

            # Tabla categorias
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    slug VARCHAR(50) NOT NULL UNIQUE,
                    icono VARCHAR(50),
                    color VARCHAR(7) DEFAULT '#3388ff',
                    descripcion TEXT
                )
            """))
            print("   ✓ Tabla 'categorias' creada")

            # Tabla etiquetas_especiales
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS etiquetas_especiales (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    slug VARCHAR(50) NOT NULL UNIQUE,
                    icono VARCHAR(50),
                    color VARCHAR(7) DEFAULT '#28a745',
                    descripcion TEXT
                )
            """))
            print("   ✓ Tabla 'etiquetas_especiales' creada")

            # Tabla lugar_categorias (many-to-many)
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS lugar_categorias (
                    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
                    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
                    PRIMARY KEY (lugar_id, categoria_id)
                )
            """))
            print("   ✓ Tabla 'lugar_categorias' creada")

            # Tabla lugar_etiquetas (many-to-many)
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS lugar_etiquetas (
                    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
                    etiqueta_id INTEGER NOT NULL REFERENCES etiquetas_especiales(id) ON DELETE CASCADE,
                    PRIMARY KEY (lugar_id, etiqueta_id)
                )
            """))
            print("   ✓ Tabla 'lugar_etiquetas' creada")

            # Tabla menus
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS menus (
                    id SERIAL PRIMARY KEY,
                    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    archivo_url VARCHAR(300),
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✓ Tabla 'menus' creada")

            # Tabla items_menu
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS items_menu (
                    id SERIAL PRIMARY KEY,
                    menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    precio DECIMAL(10, 2) NOT NULL,
                    categoria VARCHAR(50),
                    disponible BOOLEAN DEFAULT TRUE,
                    orden INTEGER DEFAULT 0
                )
            """))
            print("   ✓ Tabla 'items_menu' creada")

            # Tabla redes_sociales
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS redes_sociales (
                    id SERIAL PRIMARY KEY,
                    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
                    tipo VARCHAR(50) NOT NULL,
                    url_perfil VARCHAR(300) NOT NULL,
                    qr_code_url VARCHAR(300),
                    clics INTEGER DEFAULT 0,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✓ Tabla 'redes_sociales' creada")

            # Tabla fotos_lugar
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS fotos_lugar (
                    id SERIAL PRIMARY KEY,
                    lugar_id INTEGER NOT NULL REFERENCES lugar_sugerido(id) ON DELETE CASCADE,
                    url VARCHAR(300) NOT NULL,
                    descripcion TEXT,
                    orden INTEGER DEFAULT 0,
                    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✓ Tabla 'fotos_lugar' creada")

            print("\n2. Agregando nuevas columnas a lugar_sugerido...")

            # Agregar columnas nuevas (con IF NOT EXISTS simulado con try/except)
            nuevas_columnas = [
                ("descripcion", "TEXT"),
                ("telefono", "VARCHAR(20)"),
                ("email_contacto", "VARCHAR(150)"),
                ("sitio_web", "VARCHAR(200)"),
                ("vistas", "INTEGER DEFAULT 0"),
                ("clics_como_llegar", "INTEGER DEFAULT 0"),
                ("clics_telefono", "INTEGER DEFAULT 0"),
                ("horarios", "TEXT"),
            ]

            for columna, tipo in nuevas_columnas:
                try:
                    db.session.execute(db.text(f"""
                        ALTER TABLE lugar_sugerido
                        ADD COLUMN IF NOT EXISTS {columna} {tipo}
                    """))
                    print(f"   ✓ Columna '{columna}' agregada")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                        print(f"   - Columna '{columna}' ya existe")
                    else:
                        raise

            # Commit de todos los cambios
            db.session.commit()
            print("\n✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("\nAhora ejecuta: python3 init_categories.py")
            print("Para inicializar las categorías y etiquetas.\n")

            return True

    except Exception as e:
        print(f"\n✗ ERROR durante la migración:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
