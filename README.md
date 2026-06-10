# 🌿 EcoReport Huancayo

## Descripción

EcoReport Huancayo es una aplicación web de impacto social desarrollada en Angular que permite a los ciudadanos registrar, visualizar y hacer seguimiento de reportes sobre puntos críticos de acumulación de residuos sólidos en la ciudad de Huancayo, Perú.

---

## Problema social

La ciudad de Huancayo enfrenta una problemática creciente:

- **Acumulación de residuos sólidos** en calles, jirones y espacios públicos.
- **Botaderos informales** en zonas periféricas y riberas del río Shullcas.
- **Malos olores, plagas e inseguridad** por descomposición de residuos.
- **Falta de comunicación** entre ciudadanos y autoridades municipales.

---

## Objetivo

Desarrollar una aplicación web responsive que permita:

1. A los **ciudadanos** reportar puntos críticos con descripción, ubicación e imagen.
2. A los **validadores municipales** aprobar o rechazar reportes.
3. A los **administradores** asignar cuadrillas de limpieza.
4. Visualizar estadísticas del estado de los reportes.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Angular 18 | Framework principal (standalone components) |
| TypeScript | Tipado estático y modelos de datos |
| CSS puro | Estilos responsive sin dependencias externas |
| Angular Router | Navegación con lazy loading |
| Servicios Angular | Lógica de negocio y datos simulados |
| Leaflet + OpenStreetMap | Mapas reales, marcadores y geolocalización |

> Backend preparado para: FastAPI + PostgreSQL + JWT

---

## Rutas

| Ruta | Descripción |
|---|---|
| `/` | Landing page |
| `/login` | Inicio de sesión |
| `/registro` | Crear cuenta |
| `/reportes-publicos` | Consulta pública con filtros |
| `/mapa-ambiental` | Mapa demostrativo de incidencias |
| `/contacto` | Formulario de contacto y mesa de ayuda simulada |
| `/dashboard` | Resumen + mapa simulado |
| `/reportar` | Formulario de reporte |
| `/mis-reportes` | Historial del ciudadano |
| `/validacion` | Panel municipal |
| `/admin/usuarios` | Gestión de roles y estados de usuarios |
| `/cuadrillas` | Asignación de cuadrillas |
| `/estadisticas` | Métricas y gráficas |

---

## Instalación

```bash
npm install
ng serve
```

## Credenciales demo

Todos los usuarios usan la contraseña `123456`.

| Rol | Correo |
|---|---|
| Ciudadano | `ciudadano@ecoreport.pe` |
| Validador | `validador1@ecoreport.pe` |
| Administrador | `admin@ecoreport.pe` |

La sesión, los usuarios, los cambios de rol y los reportes se guardan en
`localStorage` para simular la persistencia mientras se integra la API REST.

---

## Integrantes

- Carhuaz Barzola Juan Abel
- Huaraca Huaraca Jhafeth Frank
- Enrique Ricce Angela Ariana

---

## Estado del proyecto — Semana 12

- [x] Estructura Angular creada
- [x] Rutas con lazy loading
- [x] Modelos TypeScript
- [x] Servicios simulados
- [x] Sesión persistente y menús por rol
- [x] Validación y administración funcional en modo prototipo
- [x] Componentes compartidos
- [x] 9 páginas implementadas
- [x] Diseño responsive
- [x] Preparado para FastAPI + PostgreSQL

---

Proyecto universitario — Programación Web 2026
