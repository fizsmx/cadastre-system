# Catastro Contribuyentes

Módulo especializado para el sistema de Catastro Municipal. 
Este módulo adapta la funcionalidad base de contactos de Odoo para convertirla en un Padrón Municipal de Contribuyentes completo.

## Características

* Separación de Contribuyentes (Persona Natural vs. Empresa)
* Asignación automática del Padrón Municipal de Contribuyentes (PMC) mediante secuencias
* Registro exhaustivo de nombres (Paterno, Materno, Casada, Nombres)
* Detalles domiciliarios (Departamento, Ciudad, Barrio, Vía, etc.)
* Reglas de validación y unicidad de documentos (NIT, CI)
* Interfaz renovada (renombramiento de Contactos a Contribuyentes) y vistas condicionales

## Requisitos
* Depende de los módulos `base` y `contacts`.

## Migración
Se incluye un script de migración (`migrate.py`) capaz de leer datos desde la estructura de tabla antigua (`contribuyentes` en PostgreSQL) y adaptarlos a esta nueva arquitectura, generando correctamente los nuevos PMCs, limpiando las validaciones y formateando nombres automáticamente.

## Estructura
* `models/` - Contiene la lógica de negocio y extensión de `res.partner`.
* `views/` - Define las vistas XML condicionales y los reemplazos del menú.
* `data/` - Declaración de secuencias (`ir.sequence`) para auto-numeración.
