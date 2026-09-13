# Modelo de datos y persistencia de Gestión de Atención

## 1. Objetivo de la persistencia

Gestión de Atención necesita mantener su propia base de datos para conservar la información del agregado `Atencion` y garantizar su autonomía dentro del bounded context.

Esta persistencia es necesaria porque:

- el microservicio tiene un modelo de negocio propio
- eel agregado `Atencion` debe conservar su estado actual y la información necesaria para gestionar su ciclo de vida.
- la información de atención no debe depender de la base de datos de Solicitudes Partner
- la evolución del dominio local no debe estar acoplada a otro servicio

La persistencia propia permite que Gestión de Atención sea independiente, estable y consistente con el principio de bounded context.

## 2. Propiedad de los datos

La propiedad de los datos debe quedar claramente separada entre microservicios:

- `Gestión de Atención` es propietario de los datos de `Atencion`.
- `Solicitudes Partner` es propietario de sus propios datos y del evento que publica.
- No existe acceso directo entre bases de datos.
- No existen claves foráneas ni referencias de persistencia entre microservicios.
- La integración entre microservicios se realiza exclusivamente mediante eventos.

Esto mantiene la frontera de responsabilidad y evita acoplamientos estructurales entre bounded contexts.

## 3. Modelo lógico

La persistencia del bounded context Gestion de Atención se modela con una única tabla principal:

```text
atenciones
```

### Campos mínimos

| Campo | Tipo conceptual | Obligatorio | Propósito | Regla o restricción |
|---|---|---|---|---|
| `id_atencion` | identificador único | Sí | Identifica la atención de forma única. | Debe ser clave primaria. |
| `solicitud_id` | identificador de negocio | Sí | Relaciona la atención con la solicitud de negocio que la originó. | Debe ser único para una sola atención. |
| `partner_id` | identificador de negocio | Sí | Identifica al partner asociado a la atención. | Debe estar presente y no nulo. |
| `referencia_externa` | texto | Sí | Guarda la referencia externa asociada a la atención. | Debe estar presente y no nulo. |
| `tipo_servicio` | texto | Sí | Describe el tipo de servicio asociado. | Debe estar presente y no nulo. |
| `estado` | enumeración / texto | Sí | Representa el estado actual de la atención. | Debe ser uno de `PENDIENTE`, `EN_ATENCION`, `CERRADA`. |
| `fecha_creacion` | fecha/hora | Sí | Registra el momento de creación de la atención. | Debe estar presente y no nulo. |

## 4. Restricciones

Conceptualmente, la tabla `atenciones` debe cumplir con las siguientes restricciones:

- `id_atencion` como clave primaria
- `solicitud_id` NOT NULL
- `partner_id` NOT NULL
- `referencia_externa` NOT NULL
- `tipo_servicio` NOT NULL
- `estado` NOT NULL
- `fecha_creacion` NOT NULL
- `solicitud_id` UNIQUE para garantizar una sola atención por solicitud
- `estado` restringido a: `PENDIENTE`, `EN_ATENCION`, `CERRADA`

No se agregan columnas adicionales que no estén justificadas por el modelo actual.

## 5. Índices

Los índices necesarios para esta etapa son mínimos y orientados a la unicidad y a la consulta operativa.

### 1) UNIQUE sobre `solicitud_id`

Este índice es imprescindible para garantizar que una misma solicitud no genere dos registros de atención.

Su propósito es reforzar la regla de negocio:

- una solicitud puede generar como máximo una atención

### 2) Índice sobre `estado`

Puede resultar útil para consultas operativas de monitoreo o listados por estado, por ejemplo:

- atenciones pendientes
- atenciones en atención
- atenciones cerradas

No es obligatorio para la regla de negocio principal, pero sí tiene valor para consultas de operación y seguimiento del agregado.

## 6. Relación con el agregado Atencion

El modelo de persistencia es una representación del agregado `Atencion` y no debe confundirse con el modelo de dominio.

El mapeo conceptual es el siguiente:

```text
Atencion.id_atencion       -> atenciones.id_atencion
Atencion.solicitud_id      -> atenciones.solicitud_id
Atencion.partner_id        -> atenciones.partner_id
Atencion.referencia_externa -> atenciones.referencia_externa
Atencion.tipo_servicio     -> atenciones.tipo_servicio
Atencion.estado            -> atenciones.estado
Atencion.fecha_creacion    -> atenciones.fecha_creacion
```

La base de datos almacena el estado del agregado, pero no reemplaza la lógica de dominio. La persistencia debe reflejar la estructura del agregado y respetar sus invariantes.

## 7. Idempotencia

La base de datos puede apoyar la idempotencia del procesamiento del evento `SolicitudPartnerRegistrada.v1`.

La regla de negocio es la siguiente:

- un mismo `solicitud_id` no puede generar dos registros de atención

Esto se protege con la restricción `UNIQUE` sobre `solicitud_id`.

Esto significa que si un evento se reentrega o se procesa dos veces con la misma `solicitud_id`, la persistencia impide la creación de un segundo registro.

Este mecanismo ayuda a la estrategia de idempotencia, pero la estrategia completa de deduplicación y manejo de reintentos corresponde a la capa de aplicación e infraestructura en etapas posteriores.

## 8. Flujo de persistencia esperado

El flujo conceptual de persistencia es:

```text
SolicitudPartnerRegistrada.v1
        ↓
Consumer
        ↓
Aplicación
        ↓
Crear Atencion
        ↓
Repository
        ↓
PostgreSQL
        ↓
Persistencia exitosa
        ↓
ACK del mensaje
```

La clave del flujo es que el `ACK` del mensaje solo se realiza después de una persistencia exitosa.

Si la operación falla antes de persistir, el mensaje debería poder volver a procesarse según la estrategia que se defina posteriormente.

## 9. Decisión sobre topología de datos

La topología de datos para este contexto es descentralizada:

- cada microservicio posee sus datos
- no existe una base de datos compartida
- se evita el acoplamiento estructural entre bounded contexts
- la información necesaria llega mediante Integration Events

Esto es coherente con DDD y con el enfoque de bounded contexts: cada microservicio conserva su propio modelo y su propia persistencia, y la integración ocurre por eventos y contratos explícitos.

## 10. Trade-offs

### Ventajas

- autonomía del microservicio
- menor acoplamiento
- independencia de evolución del modelo local
- facilita la escalabilidad independiente

### Costos

- posible duplicación de información
- consistencia eventual
- necesidad de manejar idempotencia
- mayor complejidad de integración

## 11. Fuera de alcance

En este momento no se implementan ni diseñan:

- tablas adicionales
- Event Sourcing
- CQRS completo
- auditoría avanzada
- histórico de estados
- FK hacia otros microservicios
- sincronización directa con Solicitudes Partner

Este documento define únicamente el modelo mínimo de persistencia para el bounded context de Gestión de Atención.

## 12. Decisión final

Gestión de Atención utilizará una base de datos propia con PostgreSQL como almacenamiento del agregado `Atencion`.

La representación mínima será una tabla llamada `atenciones`, con los campos estrictamente necesarios para mantener el ciclo de vida de la atención y la regla de unicidad por `solicitud_id`.

La integración con otros microservicios seguirá siendo exclusivamente mediante eventos, sin compartir bases de datos ni crear dependencias directas entre persistent layers.

## Validación

Se ha creado el documento solicitado en:

- `docs/04-modelo-datos-y-persistencia.md`

Se valida que:

1. el documento describe solo diseño de persistencia y modelo de datos
2. no se implementa PostgreSQL ni infraestructura real
3. no se modifica el dominio existente
4. no se agregan campos fuera del modelo actual
5. la propuesta es coherente con la autonomía del bounded context y con el evento `SolicitudPartnerRegistrada.v1`

### Archivos modificados

- `docs/04-modelo-datos-y-persistencia.md`
