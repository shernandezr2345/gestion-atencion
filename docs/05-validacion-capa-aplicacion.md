# Validación de la capa de aplicación: Gestión de Atención

## Objetivo

Validar que la capa de aplicación implementada para el bounded context de Gestión de Atención cumple con la intención arquitectónica definida para esta etapa, sin introducir reglas del dominio, infraestructura ni integración técnica que no correspondan a este bloque.

Este documento es una validación de diseño y comportamiento de la capa de aplicación, no una ampliación de la implementación.

## 1. Verificación del diseño de la capa de aplicación

Se revisa la estructura definida para la capa de aplicación:

- `src/gestion_atencion/modulos/atencion/aplicacion/servicios.py`
- `src/gestion_atencion/modulos/atencion/aplicacion/excepciones.py`
- `docs/05-capa-aplicacion.md`

Se valida que la capa de aplicación cumple con su responsabilidad principal:

- coordinar casos de uso;
- orquestar flujo entre entrada, dominio y repositorio;
- no incluir reglas del agregado;
- no decidir las transiciones de estado;
- no conocer detalles de PostgreSQL, Pulsar, Avro ni API.

Resultado: la capa de aplicación cumple con el rol esperado de coordinación.

## 2. Verificación del caso de uso Crear Atención

Se verifica el caso de uso `CrearAtencion`.

### Flujo validado

1. recibe la información necesaria para crear la atención;
2. consulta si ya existe una atención para la misma `solicitud_id`;
3. si existe, evita la creación duplicada;
4. si no existe, crea el agregado con `Atencion.crear(...)`;
5. persiste a través del `Repository`;
6. devuelve la entidad creada.

### Evaluación

La lógica de negocio no se duplicó en la aplicación. La aplicación solo coordina y delega.

La validación de la existencia de la Atención se hace por `solicitud_id`, que es la regla de idempotencia inicial definida para esta etapa.

No se implementa deduplicación distribuida ni `event_id`, como correspondía al alcance solicitado.

Resultado: el caso de uso de creación está alineado con el diseño documentado.

## 3. Verificación del caso de uso Cambiar Estado

Se verifica el caso de uso `CambiarEstadoAtencion`.

### Flujo validado

1. recibe el identificador de la atención y el nuevo estado;
2. busca la atención por `solicitud_id`;
3. si no existe, lanza la excepción de atención no encontrada;
4. invoca el método del dominio correspondiente;
5. deja que el agregado valide la transición;
6. actualiza el registro mediante el `Repository`;
7. devuelve la atención actualizada.

### Evaluación

La capa de aplicación no decide si una transición es válida. Esa decisión se delega a `Atencion`.

Las transiciones permitidas permanecen:

- `PENDIENTE -> EN_ATENCION`
- `EN_ATENCION -> CERRADA`

Esto cumple con la regla del dominio y respeta la separación de responsabilidades.

Resultado: la aplicación orquesta, pero no reemplaza la lógica del dominio.

## 4. Verificación de la separación de responsabilidades

Se valida la estructura de dependencias:

```text
Entrada
   ↓
Application
   ↓
Domain
   ↓
Repository
   ↓
Infrastructure
```

### Se cumple que:

- `Application` coordina casos de uso;
- `Domain` contiene the reglas de negocio y el agregado;
- `Repository` sigue siendo la abstracción de persistencia;
- `Infrastructure` sigue siendo la implementación técnica de PostgreSQL.

### Se evita que:

- `Application` dependa directamente de PostgreSQL;
- `Application` dependa de SQL;
- `Application` dependa de Pulsar o Avro;
- `Domain` dependa de Application o Infrastructure.

Resultado: la separación arquitectónica es correcta y coherente con Dependency Inversion.

## 5. Verificación del manejo de errores

Se revisan las excepciones definidas en la capa de aplicación:

- `AtencionNoEncontradaError`
- `AtencionYaExisteError`
- `ErrorAplicacionAtencion` como base de la capa

Se valida que los errores se usan para distinguir:

- atención no encontrada;
- atención ya existente;
- flujo de aplicación fuera de condiciones esperadas.

Se mantiene la regla de no ocultar errores técnicos con `except Exception` genérico dentro de la lógica de aplicación.

Resultado: el manejo de errores es específico y no convierte problemas técnicos en errores de negocio.

## 6. Verificación de tests de aplicación

Se revisan los tests creados para la capa de aplicación:

- `tests/unitarias/test_aplicacion_atencion.py`

Se validan los escenarios mínimos pedidos:

1. crear una atención cuando no existe otra para la solicitud;
2. no crear una segunda atención si ya existe;
3. validar que los datos suministrados se usen correctamente;
4. cambiar `PENDIENTE -> EN_ATENCION`;
5. cambiar `EN_ATENCION -> CERRADA`;
6. propagar una transición inválida definida por el dominio;
7. reportar atención no encontrada.

Resultado: los tests cubren los casos de uso principales y mantienen un aislamiento adecuado con un fake del repository.

## 7. Verificación de regresión

Se ejecuta la suite completa con pytest:

```bash
python -m pytest -q
```

### Resultado observado

Se obtuvieron:

- `20 passed in 0.48s`

Esto confirma que:

- no hubo regresión en el dominio;
- no hubo regresión en la persistencia;
- la capa de aplicación se integra sin romper lo anterior.

## 8. Evaluación arquitectónica

La capa de aplicación queda validada como:

- punto de coordinación del bounded context;
- orquestadora del caso de uso;
- responsable del flujo de creación y cambio de estado;
- no responsable de las reglas del dominio;
- no responsable de detalles técnicos de SQL o infraestructura.

Se confirma que la capa de aplicación cumple con la intención planteada en `docs/05-capa-aplicacion.md`.

## 9. Conclusión

La versión implementada de la capa de aplicación es coherente con la arquitectura propuesta para Gestión de Atención.

Se valida que:

- los casos de uso están cubiertos;
- la lógica del dominio permanece centralizada en `Atencion`;
- el `Repository` sigue siendo la abstracción de persistencia;
- la infraestructura no es acoplada a la capa de aplicación;
- la funcionalidad implementada no avanza a Pulsar, Avro, Consumer ni REST.

La validación de la capa 05 queda correcta y consistente con la arquitectura esperada para este bloque.
