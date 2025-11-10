# 🚨 MIGRACIÓN URGENTE - LocalHub

## Problema Actual

El sitio está mostrando un error 500 en `/mapa` porque la base de datos no tiene las nuevas tablas y columnas que requiere LocalHub.

**Error**: `sqlalchemy.exc.OperationalError`

## Solución: Aplicar Migración

Necesitas ejecutar estos comandos **en tu servidor de producción** donde está corriendo la aplicación:

### Opción 1: Usando el script de migración (RECOMENDADO)

```bash
# 1. Conectarte a tu servidor (SSH)
ssh usuario@tu-servidor.com

# 2. Ir al directorio de la aplicación
cd /ruta/a/sin-tacc-1.1

# 3. Ejecutar el script de migración
python3 apply_migration.py

# 4. Si fue exitoso, inicializar categorías y etiquetas
python3 init_categories.py

# 5. Reiniciar la aplicación
sudo systemctl restart tu-servicio
# O si usas Gunicorn:
sudo systemctl restart gunicorn
# O si usas Docker:
docker-compose restart
```

### Opción 2: Aplicar SQL manualmente

Si prefieres aplicar la migración SQL directamente a tu base de datos Neon:

```bash
# 1. Descargar el archivo SQL de migración
# (El script apply_migration.py contiene todos los comandos SQL necesarios)

# 2. Conectarte a tu base de datos Neon
psql "postgresql://tu-usuario:tu-password@ep-snowy-thunder-a4gsx6gn-pooler.us-east-1.aws.neon.tech/tu-database?sslmode=require"

# 3. O usar la interfaz web de Neon para ejecutar el SQL
```

### Opción 3: Usar Flask-Migrate (si está configurado)

```bash
cd /ruta/a/sin-tacc-1.1
flask db upgrade
```

## ¿Qué hace la migración?

La migración agrega:

### Nuevas Tablas:
- `categorias` - Para categorizar comercios (Restaurante, Cafetería, etc.)
- `etiquetas_especiales` - Para etiquetas (Sin Gluten, Vegano, etc.)
- `lugar_categorias` - Relación many-to-many lugares ↔ categorías
- `lugar_etiquetas` - Relación many-to-many lugares ↔ etiquetas
- `menus` - Menús/cartas de los comercios
- `items_menu` - Items individuales de cada menú
- `redes_sociales` - Redes sociales de los comercios
- `fotos_lugar` - Galería de fotos de los comercios

### Nuevas Columnas en `lugar_sugerido`:
- `descripcion` - Descripción del comercio
- `telefono` - Teléfono de contacto
- `email_contacto` - Email del comercio
- `sitio_web` - URL del sitio web
- `vistas` - Contador de vistas
- `clics_como_llegar` - Contador de clics en "Cómo llegar"
- `clics_telefono` - Contador de clics en teléfono
- `horarios` - Horarios de apertura (JSON)

## Verificación Post-Migración

Después de aplicar la migración, verifica que todo funcione:

1. **Accede al sitio**: https://glutymap.com/mapa
   - Debería cargar sin error 500

2. **Revisa las APIs**:
   - https://glutymap.com/api/categorias
   - https://glutymap.com/api/etiquetas

3. **Verifica el dashboard de comercios**:
   - Inicia sesión como comercio
   - Ve a "Mi Comercio" → "Dashboard"

## ¿Problemas?

Si después de aplicar la migración sigues teniendo problemas:

1. **Revisa los logs de la aplicación**:
   ```bash
   tail -f /var/log/tu-app/error.log
   # O donde estén tus logs
   ```

2. **Verifica que las tablas se crearon**:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

3. **Reinicia la aplicación completamente**:
   ```bash
   # Mata todos los procesos de Python
   sudo pkill -f "python.*app.py"

   # Reinicia el servicio
   sudo systemctl restart tu-servicio
   ```

## Rollback (Si algo sale mal)

Si necesitas revertir los cambios:

```sql
-- Solo si es absolutamente necesario
DROP TABLE IF EXISTS fotos_lugar CASCADE;
DROP TABLE IF EXISTS redes_sociales CASCADE;
DROP TABLE IF EXISTS items_menu CASCADE;
DROP TABLE IF EXISTS menus CASCADE;
DROP TABLE IF EXISTS lugar_etiquetas CASCADE;
DROP TABLE IF EXISTS lugar_categorias CASCADE;
DROP TABLE IF EXISTS etiquetas_especiales CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;

-- Revertir columnas (PostgreSQL)
ALTER TABLE lugar_sugerido
    DROP COLUMN IF EXISTS descripcion,
    DROP COLUMN IF EXISTS telefono,
    DROP COLUMN IF EXISTS email_contacto,
    DROP COLUMN IF EXISTS sitio_web,
    DROP COLUMN IF EXISTS vistas,
    DROP COLUMN IF EXISTS clics_como_llegar,
    DROP COLUMN IF EXISTS clics_telefono,
    DROP COLUMN IF EXISTS horarios;
```

## Soporte

Si tienes problemas ejecutando la migración, proporciona:

1. Los logs de error completos
2. La versión de PostgreSQL que usas
3. Si estás usando Neon, Supabase, u otro proveedor
4. El resultado de: `python3 --version` y `pip3 list | grep -i sql`

---

**IMPORTANTE**: La migración es NECESARIA para que el sitio funcione. Sin ella, verás errores 500 en múltiples páginas.
