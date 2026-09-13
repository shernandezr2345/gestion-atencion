# Validación del esquema Avro y evolución del Integration Event: SolicitudPartnerRegistrada

## Objetivo

Validar que el diseño del esquema Avro del Integration Event `SolicitudPartnerRegistrada` es coherente con:

- el contrato conceptual definido en `docs/03-contrato-evento-solicitud-partner-registrada.md`;
- la intención arquitectónica del microservicio Gestión de Atención;
- la evolución propuesta de V1 a V2;
- la separación de responsabilidades entre el productor y el consumidor;
- la restricción de no implementar infraestructura real de Pulsar ni Schema Registry en este bloque.

Este documento no implementa código ni infraestructura. Su propósito es verificar únicamente la corrección del diseño técnico documentado.

## 1. Verificación del alcance

Se revisa que el diseño del schema Avro:

- pertenece al bounded context de Gestión de Atención;
- representa un `Integration Event` de negocio;
- define un contrato externo y serializable;
- no introduce infraestructura real ni broker en este bloque;
- no agrega componentes de REST, producer, consumer o Schema Registry;
- mantiene el enfoque técnico limitado a la representación del evento.

Resultado: cumple con el alcance documental establecido para este bloque.

## 2. Verificación del nombre y la versión

El evento se define como:

- nombre: `SolicitudPartnerRegistrada`
- versión V1: `v1`
- versión V2: `v2`

La versión se mantiene consistente con la regla de evolución del contrato:

- `event_type = "SolicitudPartnerRegistrada"`
- `event_version = "v1"` para V1
- `event_type = "SolicitudPartnerRegistrada"`
- `event_version = "v2"` para V2

Esto cumple con la decisión documentada de no introducir un tercer mecanismo de versionado independiente. La versión del evento y la evolución del schema se resuelven de forma consistente mediante `event_version` y la compatibilidad del contrato.

## 3. Verificación del contrato V1

La estructura conceptual de V1 debe mantenerse mínima y estable:

```json
{
  "metadata": {
    "event_id": "string",
    "event_time": "long",
    "event_type": "string",
    "event_version": "string"
  },
  "data": {
    "solicitud_id": "string",
    "partner_id": "string",
    "referencia_externa": "string",
    "tipo_servicio": "string"
  }
}
```

Se valida que:

- `metadata` contiene la trazabilidad del evento;
- `data` contiene la información mínima de negocio;
- no se agregan campos extra en V1;
- el contrato es compatible con el mínimo requerido del negocio;
- la información corresponde al hecho de registro de la solicitud del partner.

## 4. Verificación de los campos de metadata

| Campo | Tipo Avro | Requerido | Observación |
|---|---|---:|---|
| `event_id` | `string` | Sí | Identificador único del evento |
| `event_time` | `long` | Sí | Debe representar timestamp-millis del hecho de negocio |
| `event_type` | `string` | Sí | Debe indicar el tipo del evento |
| `event_version` | `string` | Sí | Debe indicar la versión del contrato |

Se valida que `event_time` usa la representación recomendada con tipo `long` y la documentación correspondiente para indicar que representa timestamp-millis y que corresponde al momento del hecho de negocio que originó el evento.

Esto es correcto porque la intención no es registrar el instante de publicación del mensaje en el broker, sino el momento del hecho de negocio que generó la intención de integración.

## 5. Verificación de los campos de data

| Campo | Tipo Avro | Requerido | Observación |
|---|---|---:|---|
| `solicitud_id` | `string` | Sí | Identificador de la solicitud registrada |
| `partner_id` | `string` | Sí | Identificador del partner asociado |
| `referencia_externa` | `string` | Sí | Referencia externa asociada |
| `tipo_servicio` | `string` | Sí | Tipo de servicio solicitado |

Se confirma que estos son exactamente los campos mínimos definidos por el contrato de negocio y no se incorporan atributos de infraestructura, persistencia ni campo de control innecesarios.

## 6. Verificación de V2

El esquema V2 debe mantener exactamente los campos de V1 y agregar únicamente:

```json
"estado": {
  "type": ["null", "string"],
  "default": null
}
```

Se valida que:

- no se elimina ni cambia el significado de ningún campo de V1;
- `estado` se agrega como extensión compatible;
- `estado` es nullable y tiene `default: null`, como exige la evolución compatible;
- la compatibilidad del contrato se conserva para evolución incremental.

Esto es coherente con el diseño documentado y con la intención de que V2 sea una versión compatible sobre V1.

## 7. Verificación de la documentación dentro del schema

Se revisa que los schemas incluyen `doc` cuando es útil para precisar:

- qué representa el evento;
- qué representa `event_time`;
- que `event_time` corresponde al momento del hecho de negocio/origen del evento;
- que V2 agrega `estado` de forma compatible.

Resultado: la documentación embebida en los schemas cumple con el objetivo de explicar el sentido del evento y de los campos clave sin introducir elementos ajenos al contrato.

## 8. Verificación de compatibilidad y evolución

La evolución del evento debe ser controlada y compatible. La validación concluye que:

- V1 es el contrato mínimo estable;
- V2 solo agrega el campo `estado`;
- no se cambian nombres ni tipos previos;
- la compatibilidad se mantiene para consumidores que ignoran o aceptan campos nuevos;
- no se introduce un tercer nivel de versionado separado de `event_type` y `event_version`.

Esto es coherente con la idea de evolución controlada del contrato.

## 9. Verificación de la relación con el resto del documento 06

El documento 06 define una evolución conceptual del schema Avro y una decisión técnica que no obliga a implementar Pulsar ni Schema Registry en este bloque. La validación confirma que:

- el diseño de Avro se mantiene conceptualmente correcto;
- no se expande el alcance con patrones o infraestructuras adicionales;
- el event schema está alineado con el contrato de negocio definido en el documento 03;
- la versión V1 y V2 están explicitadas sin ambigüedad;
- la documentación técnica es consistente con la intención del bloque.

## 10. Verificación de restricciones del bloque

Se valida que no se introducen elementos no autorizados:

- no se implementa Apache Pulsar;
- no se implementa producer;
- no se implementa consumer;
- no se implementa Schema Registry;
- no se agregan REST endpoints;
- no se agregan nuevos patrones ni infraestructura innecesaria;
- no se expande el alcance más allá de los schemas Avro reales y su versión.

Resultado: el diseño cumple con la restricción del bloque.

## 11. Resultado de la validación

### A. Correcto

El diseño del esquema Avro de `SolicitudPartnerRegistrada` es correcto para esta etapa porque:

- define el contrato técnico mínimo y explícito;
- respeta el contrato conceptual definido en el documento 03;
- usa `event_time` como timestamp-millis del hecho de negocio;
- mantiene los metadatos mínimos necesarios;
- define V1 y V2 de forma compatible;
- agrega `estado` con nullable y default null en V2;
- mantiene una separación clara entre contrato y infraestructura.

### B. Problemas encontrados

No se encontraron problemas de diseño en el esquema Avro documentado para este bloque.

### C. Archivos involucrados

- `docs/03-contrato-evento-solicitud-partner-registrada.md`
- `docs/06-schema-avro-y-evolucion.md`
- `docs/06-validacion-schema-avro-y-evolucion.md`

### D. Recomendación

El diseño puede avanzar sin cambios en el alcance de este bloque. Se recomienda mantener la definición actual de V1 y V2 y continuar con la siguiente etapa únicamente cuando se solicite el siguiente bloque, sin expandir el diseño ni implementar infraestructura adicional.

## Conclusión

El esquema Avro propuesto para `SolicitudPartnerRegistrada` es coherente con el contrato de negocio, está versionado correctamente, evita ambigüedad en el versionado, mantiene compatibilidad de evolución y se ajusta al alcance limitado del bloque 06.
