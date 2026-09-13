# Contrato de integración: SolicitudPartnerRegistrada.v1

## 1. Objetivo del evento

`SolicitudPartnerRegistrada.v1` es un Integration Event que comunica que una solicitud de partner fue registrada y queda disponible para que otros bounded contexts reaccionen a ese hecho.

Este evento es relevante para Gestión de Atención porque permite que el microservicio reciba una señal de negocio sin consultar directamente la base de datos de Solicitudes Partner.

El consumidor de este evento no necesita conocer el modelo interno de dominio del productor. Solo necesita los datos mínimos del contrato de integración para crear o actualizar su propio modelo local.

## 2. Tipo de evento

Este evento es un `Integration Event`.

Un `Integration Event` se usa para comunicar hechos entre microservicios o bounded contexts.

Un `Domain Event` interno, en cambio, se usa dentro del mismo modelo de dominio para representar un cambio significativo del agregado y suele ser parte del diseño del dominio local.

La diferencia clave es:

- `Domain Event`: comunica cambios dentro del mismo microservicio
- `Integration Event`: comunica hechos entre microservicios

En este caso, `SolicitudPartnerRegistrada.v1` representa un hecho de integración, no un evento interno del dominio de Gestión de Atención.

## 3. Nombre y versión

- Nombre del evento: `SolicitudPartnerRegistrada`
- Versión: `v1`
- Identificador completo: `SolicitudPartnerRegistrada.v1`

## 4. Estructura del mensaje

```json
{
  "metadata": {
    "event_id": "string",
    "event_time": "timestamp",
    "event_type": "SolicitudPartnerRegistrada.v1",
    "event_version": "v1"
  },
  "data": {
    "solicitud_id": "string",
    "partner_id": "string",
    "referencia_externa": "string",
    "tipo_servicio": "string"
  }
}
```

## 5. Tabla de campos

| Nombre | Ubicación | Tipo conceptual | Obligatorio | Descripción | Origen del dato |
|---|---|---|---|---|---|
| `event_id` | `metadata` | identificador único | Sí | Identifica de forma única la instancia del evento publicado. | infraestructura / outbox |
| `event_time` | `metadata` | fecha/hora | Sí | Momento en que ocurrió el hecho de negocio. | evento de dominio o timestamp del productor |
| `event_type` | `metadata` | texto | Sí | Nombre y versión del tipo de evento. | contrato de integración |
| `event_version` | `metadata` | texto | Sí | Versión del contrato. | versión del esquema/contrato |
| `solicitud_id` | `data` | identificador de negocio | Sí | Identifica la solicitud registrada. | Solicitudes Partner |
| `partner_id` | `data` | identificador de negocio | Sí | Identifica al partner asociado a la solicitud. | Solicitudes Partner |
| `referencia_externa` | `data` | texto | Sí | Referencia externa asociada a la solicitud. | Solicitudes Partner |
| `tipo_servicio` | `data` | texto | Sí | Tipo de servicio asociado a la solicitud. | Solicitudes Partner |

## 6. Mapeo conceptual desde Solicitudes Partner

La siguiente relación conceptual describe cómo se materializa el contrato de integración desde el productor:

```text
metadata:
  event_id       <- identificador del evento generado por infraestructura/outbox
  event_time     <- ocurrido_en del evento de dominio
  event_type     <- tipo del Integration Event
  event_version  <- versión del contrato

data:
  solicitud_id        <- solicitud registrada
  partner_id          <- partner asociado
  referencia_externa  <- referencia externa
  tipo_servicio       <- tipo de servicio
```

Estos datos representan el contrato de integración entre microservicios y no implican compartir la base de datos ni acceder directamente a la persistencia del otro bounded context.

La separación se mantiene por diseño:

- Solicitudes Partner publica un evento
- Gestión de Atención lo consume
- Gestión de Atención crea su propio modelo local de atención
- cada microservicio conserva la propiedad de sus propios datos

## 7. Reglas del contrato

- Los campos existentes de V1 no deben eliminarse ni cambiar de significado.
- Los consumidores deben poder procesar el evento sin conocer el modelo interno del productor.
- `solicitud_id` debe permitir identificar la solicitud de negocio.
- `event_id` debe permitir identificar de forma única la instancia del evento.
- La versión debe formar parte del contrato.
- El contrato debe ser estable en su firma principal, aunque el modelo interno del productor evolucione.
- El evento no debe incluir información de persistencia o estructura interna del productor.

## 8. Evolución del contrato

El contrato puede evolucionar en versiones. Un ejemplo compatible de evolución es:

### `SolicitudPartnerRegistrada.v2`

```json
{
  "metadata": {
    "event_id": "string",
    "event_time": "timestamp",
    "event_type": "SolicitudPartnerRegistrada.v2",
    "event_version": "v2"
  },
  "data": {
    "solicitud_id": "string",
    "partner_id": "string",
    "referencia_externa": "string",
    "tipo_servicio": "string",
    "estado": "string"
  }
}
```

En este caso, se agrega únicamente:

- `data.estado`

Este cambio es compatible con consumidores V1 si el consumidor trata el campo nuevo como opcional o ignora campos no esperados en su proceso. Sin embargo, eliminar o cambiar el significado de un campo existente sería un cambio incompatible.

## 9. Compatibilidad

| Cambio | Compatible | Motivo |
|---|---|---|
| Agregar campo opcional | Sí | No rompe el contrato existente y puede ser ignorado por consumidores anteriores. |
| Eliminar campo | No | Rompe el contrato para consumidores que dependían del campo. |
| Cambiar tipo de campo | No | Cambia la semántica y puede producir errores de deserialización o interpretación. |
| Cambiar significado de campo | No | Los consumidores ya no interpretan el dato de la misma manera. |
| Agregar nueva versión | Sí, si se mantiene compatibilidad | Permite evolucionar el contrato sin romper a consumidores existentes. |

## 10. Relación con Gestión de Atención

Cuando Gestión de Atención recibe `SolicitudPartnerRegistrada.v1`, el flujo objetivo conceptual es el siguiente:

```text
Pulsar
   ↓
Consumer
   ↓
Deserialización del evento
   ↓
Aplicación
   ↓
Crear Atencion
   ↓
Persistir en BD propia
   ↓
ACK
```

Este flujo es solamente objetivo y documental. No se implementa ni se diseña infraestructura real en este documento.

Lo importante es que el evento permite iniciar la creación del agregado `Atencion` en el bounded context local, usando la información mínima del contrato sin depender de la base de datos del productor.

## 11. Decisiones y trade-offs

### Por qué usar un Integration Event

Porque permite desacoplar microservicios y evitar dependencias directas de base de datos entre contextos.

### Por qué versionamos el contrato

Porque los eventos deben evolucionar sin romper consumidores actuales. La versión hace explícita la compatibilidad y el nivel de cambio del contrato.

### Por qué no incluimos estado en V1

Porque el evento representa la intención de registro de la solicitud y no necesariamente el estado final del negocio. En V1, el contrato debe ser mínimo y estable; el estado puede agregarse en una versión posterior.

### Por qué no exponemos entidades completas del productor

Porque el contrato debe ser un intercambio de hechos de negocio, no una copia de la estructura interna del productor. Esto reduce acoplamiento y protege la autonomía del bounded context.

### Por qué el contrato debe ser estable aunque cambie el modelo interno del productor

Porque los consumidores deben depender del contrato externo y no del modelo interno del productor. Esto permite evolucionar cada microservicio de forma independiente.

## 12. Fuera del contrato V1

Los siguientes elementos quedan fuera del contrato V1 y no se agregan en este documento:

- `correlation_id`
- `causation_id`
- `producer_service`
- `estado`
- `prioridad`
- `operador`
- `canal`
- cualquier otra extensión de negocio o infraestructura que no forme parte del payload mínimo del evento de registro

Estos elementos pueden considerarse en futuras versiones del evento, pero no forman parte de la definición V1 del contrato.

## 13. Conclusión

`SolicitudPartnerRegistrada.v1` es el contrato de integración mínimo y estable que permite a Gestión de Atención reaccionar ante la creación de una solicitud de partner sin depender de la base de datos del productor.

El evento encapsula la información necesaria para crear la atención local, mantiene el desacoplamiento entre microservicios y deja abierta la evolución del contrato mediante versiones compatibles.

## Validación

Se ha creado el documento solicitado en:

- `docs/03-contrato-evento-solicitud-partner-registrada.md`

Se valida que:

1. el documento describe únicamente el diseño del contrato
2. no se implementa código ni infraestructura
3. no se modifica `solicitud-partner`
4. no se agregan campos no autorizados en V1
5. el evento es consistente con la arquitectura del microservicio Gestión de Atención

### Archivos modificados

- `docs/03-contrato-evento-solicitud-partner-registrada.md`
