-- ============================================================
-- EcoReport - RESTORE: Restaura el estado original de las tablas
-- Ejecuta esto DESPUÉS de hacer pruebas en la API
-- ============================================================

-- Verificar que existan los backups
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__bak_usuarios')
   OR NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__bak_reportes')
   OR NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__bak_historial_reportes')
   OR NOT EXISTS (SELECT * FROM sys.tables WHERE name = '__bak_cuadrillas')
BEGIN
    RAISERROR('No se encontraron tablas de backup. Ejecuta primero backup_test.sql', 16, 1);
    RETURN;
END

BEGIN TRANSACTION;

-- Desactivar FK temporalmente para poder limpiar en orden
ALTER TABLE historial_reportes NOCHECK CONSTRAINT ALL;
ALTER TABLE reportes NOCHECK CONSTRAINT ALL;

-- Limpiar datos actuales
DELETE FROM historial_reportes;
DELETE FROM reportes;
DELETE FROM cuadrillas;
DELETE FROM usuarios;

-- Restaurar desde backup
INSERT INTO usuarios SELECT * FROM __bak_usuarios;
INSERT INTO reportes SELECT * FROM __bak_reportes;
INSERT INTO historial_reportes SELECT * FROM __bak_historial_reportes;
INSERT INTO cuadrillas SELECT * FROM __bak_cuadrillas;

-- Reactivar FK
ALTER TABLE historial_reportes CHECK CONSTRAINT ALL;
ALTER TABLE reportes CHECK CONSTRAINT ALL;

-- Eliminar tablas de backup
DROP TABLE __bak_usuarios;
DROP TABLE __bak_reportes;
DROP TABLE __bak_historial_reportes;
DROP TABLE __bak_cuadrillas;

COMMIT;

-- Mostrar resumen
SELECT 'RESTAURACIÓN COMPLETADA' as mensaje,
       (SELECT COUNT(*) FROM usuarios) as usuarios,
       (SELECT COUNT(*) FROM reportes) as reportes,
       (SELECT COUNT(*) FROM historial_reportes) as historial,
       (SELECT COUNT(*) FROM cuadrillas) as cuadrillas;
