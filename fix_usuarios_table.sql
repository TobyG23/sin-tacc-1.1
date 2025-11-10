-- Agregar columnas nuevas a la tabla usuarios
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS plan VARCHAR(20) DEFAULT 'gratuito';
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS fecha_expiracion_plan DATE;

-- Actualizar usuarios existentes para que tengan el plan gratuito
UPDATE usuarios SET plan = 'gratuito' WHERE plan IS NULL;
