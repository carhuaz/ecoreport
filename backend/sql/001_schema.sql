-- ============================================================
-- EcoReport DB - Esquema completo (tablas + migraciones)
-- Ejecutar en: EcoReportDB
-- ============================================================

-- 1. TABLAS PRINCIPALES
-- ============================================================

CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    dni NVARCHAR(8) NOT NULL UNIQUE,
    rol NVARCHAR(20) NOT NULL CHECK (rol IN ('Ciudadano', 'Validador', 'Administrador')),
    activo BIT NOT NULL DEFAULT 1,
    codigo_verificacion NVARCHAR(60) NULL,
    esta_verificado BIT NOT NULL DEFAULT 0,
    fecha_registro DATE NOT NULL DEFAULT GETDATE()
);

CREATE TABLE cuadrillas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    responsable NVARCHAR(100) NOT NULL,
    estado NVARCHAR(20) NOT NULL DEFAULT 'Disponible' CHECK (estado IN ('Disponible', 'En ruta', 'Ocupada')),
    zona_asignada NVARCHAR(200),
    distrito NVARCHAR(50) NOT NULL
);

CREATE TABLE reportes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(200) NOT NULL,
    descripcion NVARCHAR(MAX),
    distrito NVARCHAR(50) NOT NULL,
    direccion NVARCHAR(200),
    estado NVARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    prioridad NVARCHAR(20) NOT NULL DEFAULT 'Baja' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Crítica')),
    puntaje_prioridad INT NOT NULL DEFAULT 0,
    criterios_prioridad NVARCHAR(MAX),
    prioridad_corregida BIT NOT NULL DEFAULT 0,
    observacion_prioridad NVARCHAR(MAX),
    fecha DATE NOT NULL DEFAULT GETDATE(),
    latitud FLOAT,
    longitud FLOAT,
    imagenes NVARCHAR(MAX),
    ciudadano_id INT REFERENCES usuarios(id),
    observacion_validacion NVARCHAR(MAX),
    cuadrilla_id INT REFERENCES cuadrillas(id),
    anonimo BIT NOT NULL DEFAULT 0
);

CREATE TABLE historial_reportes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reporte_id INT NOT NULL REFERENCES reportes(id),
    fecha DATE NOT NULL DEFAULT GETDATE(),
    accion NVARCHAR(100) NOT NULL,
    usuario NVARCHAR(100) NOT NULL,
    observacion NVARCHAR(MAX)
);
