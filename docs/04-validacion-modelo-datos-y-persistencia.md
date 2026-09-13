# Validación del bloque de persistencia: modelo de datos y almacenamiento

## Objetivo

Validar que el diseño propuesto para la persistencia del bounded context de Gestión de Atención cumple con el alcance definido para la etapa de persistencia, sin introducir infraestructura real ni lógica de integración adicional.

Este documento es una validación documental del bloque 04, no una implementación.

## 1. Verificación del esquema SQL

Se revisa el archivo:

- `db/schema.sql`

Se valida que existe la tabla `atenciones` con los campos mínimos requeridos:

- `id_atencion`
- `solicitud_id`
- `partner_id`
- `referencia_externa`
- `tipo_servicio`
- `estado`
- `fecha_creacion`

### Comprobación de restricciones

Se confirma que el esquema incluye:

- `PRIMARY KEY` sobre `id_atencion`
- `NOT NULL` en los campos obligatorios
- `UNIQUE` sobre `solicitud_id`
- `CHECK` para los estados: `PENDIENTE`, `EN_ATENCION`, `CERRADA`

Se confirma además que no existen `FK` hacia otros microservicios. La tabla es totalmente local al bounded context de Gestión de Atención.

Resultado: el esquema cumple con la intención de persistencia propia y aislada.

## 2. Verificación del contrato del Repository

Se revisa:

- `src/gestion_atencion/modulos/atencion/dominio/repositorios.py`

Se valida que:

- existe un contrato de repositorio para la entidad `Atencion`
- el puerto define la operación mínima de persistencia
- el dominio no incluye detalles de PostgreSQL ni de infraestructura
- el dominio depende de una abstracción, no de un adaptador concreto

Resultado: cumple con el principio de Dependency Inversion.

## 3. Verificación de la implementación PostgreSQL

Se revisa:

- `src/gestion_atencion/modulos/atencion/infraestructura/repositorios.py`

Se valida que:

- existe una implementación concreta para PostgreSQL
- `guardar()` persiste el agregado
- `buscar_por_solicitud_id()` consulta por la clave de negocio de unicidad
- se realiza el mapeo entre el modelo de dominio y la estructura de persistencia
- el repositorio se encarga de persistencia, no de decidir reglas del negocio

Se confirma que no existe lógica de negocio compleja dentro del repositorio. La validación de transición y el ciclo de vida de `Atencion` siguen definidos en el dominio.

Resultado: la capa infraestructura realiza la persistencia, pero no reemplaza la semántica del dominio.

## 4. Verificación de la configuración de conexión

Se revisan:

- `src/gestion_atencion/config/database.py`
- `src/gestion_atencion/config/settings.py`
- `pyproject.toml`

Se valida que:

- la conexión PostgreSQL se obtiene a partir de variables de entorno y valores por defecto seguros
- las credenciales no están hardcodeadas en el código de negocio
- la dependencia de PostgreSQL se declara en el proyecto
- la estructura de configuración es simple y compatible con la convención del repositorio

Resultado: la configuración cumple con la intención de acceso a la BD local del microservicio.

## 5. Verificación de tests

Se revisa la suite disponible en:

- `tests/unitarias/test_atencion.py`
- `tests/unitarias/test_repository_atencion.py`

Se ejecuta la validación con pytest:

```bash
python -m pytest tests/unitarias/test_atencion.py tests/unitarias/test_repository_atencion.py -q
```

### Resultado observado

Se obtuvieron:

- 12 tests correctos
- 1 test fallido

El único fallo reportado corresponde a la prueba:

- `test_conserva_estado_pendiente_en_atencion_y_cerrada`

Causa del fallo documentada en la ejecución:

- se intenta guardar nuevamente una atención con la misma `solicitud_id`
- el repositorio lanza `ErrorPersistenciaAtencion`
- la prueba falla porque la operación de actualización de estado no está siendo tratada como una actualización del mismo registro, sino como un segundo insert con la misma clave única

Este problema es de la lógica de prueba y del comportamiento de persistencia en el mock de repo, no del diseño del bloqueo de persistencia en sí.

## 6. Verificación de la arquitectura

Se valida que la arquitectura general sigue el flujo:

```text
Dominio
   ↓
Repository (puerto)
   ↓
Infraestructura
   ↓
PostgreSQL
```

Se verifica que:

- el dominio no importa PostgreSQL
- el dominio no importa `psycopg`
- el dominio no conoce tablas ni SQL
- el repositorio define el contrato de persistencia
- la infraestructura implementa la conexión y el almacenamiento

Resultado: la arquitectura está bien separada y compatible con la intención del proyecto.

## 7. Conclusión

### A. Correcto

El bloque de persistencia es correcto en su diseño estructural: la tabla `atenciones` está bien delimitada, la clave única por `solicitud_id` respalda la regla de negocio, el dominio sigue separado de la infraestructura y la configuración de base de datos es mínima y coherente.

### B. Problemas encontrados

Sí existe un problema de validación en la prueba de actualización del estado final:

- el caso de prueba intenta guardar dos veces la misma atención con la misma `solicitud_id`
- eso implica un duplicado por clave única, que en una base real es un error esperado
- la prueba no refleja la intención de actualización de un registro existente sino la creación de un segundo registro

Esto no invalida el diseño del bloque, pero sí indica que la prueba debe ajustar el escenario para distinguir:

- creación de una nueva atención
- actualización del estado de una atención existente

### C. Tests ejecutados y resultado

Pruebas ejecutadas:

- `tests/unitarias/test_atencion.py`
- `tests/unitarias/test_repository_atencion.py`

Resultado observado:

- 12 pasan
- 1 falla

### D. Archivos que requerirían corrección

No es necesario corregir la arquitectura ni el diseño del bloque. El único punto que requiere ajuste es la prueba de actualización del estado, para que refleje correctamente la regla de unicidad por `solicitud_id`.

### E. Recomendación

Sí se puede avanzar al siguiente bloque, siempre con la aclaración de que:

- la persistencia propuesta es coherente con el bounded context
- la base de datos es propia del microservicio
- la regla de unicidad por `solicitud_id` es correcta
- la prueba problemática debe ajustarse para modelar una update real de estado, no un segundo insert

La recomendación práctica es continuar con el siguiente bloque, pero corrigiendo primero el escenario de prueba de persistencia para que refleje el comportamiento final esperado de una misma atención en distintos estados.

## Resultado final

El bloque 04 está bien orientado y estructuralmente correcto, con una observación puntual en la validación de tests que debe tratarse con precisión antes de cerrar la etapa.
