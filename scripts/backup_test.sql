-- ============================================================
-- EcoReport - BACKUP: Guarda el estado actual de las tablas
-- Ejecuta esto ANTES de hacer pruebas en la API
-- ============================================================

-- Eliminar backups anteriores si existen
DROP TABLE IF EXISTS __bak_usuarios;
DROP TABLE IF EXISTS __bak_reportes;
DROP TABLE IF EXISTS __bak_historial_reportes;
DROP TABLE IF EXISTS __bak_cuadrillas;

-- Backup de cada tabla
SELECT * INTO __bak_usuarios FROM usuarios;
SELECT * INTO __bak_reportes FROM reportes;
SELECT * INTO __bak_historial_reportes FROM historial_reportes;
SELECT * INTO __bak_cuadrillas FROM cuadrillas;

-- Mostrar resumen
SELECT 'BACKUP COMPLETADO' as mensaje,
       (SELECT COUNT(*) FROM __bak_usuarios) as usuarios,
       (SELECT COUNT(*) FROM __bak_reportes) as reportes,
       (SELECT COUNT(*) FROM __bak_historial_reportes) as historial,
       (SELECT COUNT(*) FROM __bak_cuadrillas) as cuadrillas;
