-- Script SQL para crear la tabla de tareas en Supabase
-- Copia y pega esto en: SQL Editor de Supabase

-- 1. Crear la tabla
CREATE TABLE IF NOT EXISTS tareas (
    id BIGSERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    fecha_objetivo DATE NOT NULL,
    estado TEXT NOT NULL,
    autor TEXT NOT NULL,
    asignado TEXT NOT NULL,
    cliente TEXT NOT NULL,
    comentarios TEXT DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_tareas_asignado ON tareas(asignado);
CREATE INDEX IF NOT EXISTS idx_tareas_fecha ON tareas(fecha_objetivo);
CREATE INDEX IF NOT EXISTS idx_tareas_estado ON tareas(estado);

-- 3. Habilitar Row Level Security
ALTER TABLE tareas ENABLE ROW LEVEL SECURITY;

-- 4. Crear políticas de acceso (permite todo para simplicidad)
-- En producción deberías hacer políticas más restrictivas

-- Política de SELECT (leer)
CREATE POLICY "Permitir SELECT para todos"
ON tareas FOR SELECT
USING (true);

-- Política de INSERT (crear)
CREATE POLICY "Permitir INSERT para todos"
ON tareas FOR INSERT
WITH CHECK (true);

-- Política de UPDATE (actualizar)
CREATE POLICY "Permitir UPDATE para todos"
ON tareas FOR UPDATE
USING (true)
WITH CHECK (true);

-- Política de DELETE (eliminar)
CREATE POLICY "Permitir DELETE para todos"
ON tareas FOR DELETE
USING (true);

-- 5. Insertar datos de ejemplo (opcional)
INSERT INTO tareas (descripcion, fecha_objetivo, estado, autor, asignado, cliente, comentarios)
VALUES 
    ('Revisión final contrato soporte anual', CURRENT_DATE, 'En Proceso', 'Gerente de Proyectos', 'Julio Yroba', 'Innova SA', '[]'),
    ('Validar backlog Q4 con equipo técnico', CURRENT_DATE + INTERVAL '1 day', 'Pendiente', 'Gerente de Proyectos', 'José Quintero', 'Norte Digital', '[]'),
    ('Actualizar cronograma integración ERP', CURRENT_DATE + INTERVAL '2 days', 'Pendiente', 'Julio Yroba', 'Matías Riquelme', 'MetalSur', '[]'),
    ('Informe de avance para comité mensual', CURRENT_DATE + INTERVAL '3 days', 'En Proceso', 'José Quintero', 'José Quintero', 'Gerencia Interna', '[]'),
    ('Kickoff mejora dashboard comercial', CURRENT_DATE, 'Pendiente', 'Julio Yroba', 'Julio Yroba', 'Comercial Plus', '[]');

-- Verificar que todo se creó correctamente
SELECT 'Tabla creada exitosamente' AS mensaje;
SELECT * FROM tareas ORDER BY id;
