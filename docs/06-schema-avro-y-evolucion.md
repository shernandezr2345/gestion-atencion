**# Esquema Avro y evolución del Integration Event \`SolicitudPartnerRegistrada\`**

**## 1. Objetivo**

Documentar cómo el Integration Event definido en:

\- \`docs/03-contrato-evento-solicitud-partner-registrada.md\`

será representado técnicamente utilizando Apache Avro.

Este documento explica la decisión técnica de definir un esquema estructurado para el evento, permitiendo una representación serializable, explícita y evolucionable del contrato.

La intención no es implementar Pulsar ni Avro todavía, sino dejar el diseño técnico claro para el siguiente bloque.

**## 2. Decisión tecnológica**

**### 2.1 Formato**

\- Formato de esquema: Apache Avro

\- Broker futuro: Apache Pulsar

\- Gestión de schema: Pulsar Schema Registry

Avro es adecuado para este objetivo porque:

\- define el contrato de forma explícita;

\- usa tipado fuerte;

\- ofrece serialización eficiente;

\- facilita compatibilidad entre versiones del schema;

\- encaja bien con el ecosistema de Pulsar;

\- permite demostrar una evolución controlada de \`V1\` a \`V2\`.

No se hacen afirmaciones cuantitativas de rendimiento ni de latencia, porque aún no se han medido en este proyecto.

**## 3. Relación entre contrato conceptual y schema**

**### 3.1 Contrato conceptual**

El contrato conceptual del evento es un acuerdo de negocio sobre qué información debe transmitirse.

En este caso, el evento se denomina:

- `SolicitudPartnerRegistrada`

y tiene una estructura conceptual de:

\- \`metadata\`

\- \`data\`

**### 3.2 Schema Avro**

El schema Avro es la representación técnica serializable del mismo contrato.

Su función es definir, de manera formal, el formato del payload para:

\- productor;

\- broker;

\- consumidor;

\- validación de compatibilidad.

El schema técnico no debe exponer detalles internos del microservicio ni estructuras de PostgreSQL, ni clases Python del productor.

Debe representar un contrato de integración independiente de la implementación interna.

**## 4. Definir conceptualmente el schema V1**

El event schema debe separar metadata y payload de negocio.

**### 4.1 Metadata**

La sección \`metadata\` agrupa información del evento para trazabilidad y control.

\| Campo | Tipo Avro propuesto | Obligatorio | Significado |

\| --- | --- | --- | --- |

\| \`event\_id\` | \`string\` | Sí | Identificador único del evento |

| `event_time` | `long` o `timestamp-millis` | Sí | Momento en que ocurrió el hecho de negocio que origina el evento. Corresponde al `ocurrido_en` del evento de dominio. |

| `event_type` | `string` | Sí | Nombre del tipo de evento, por ejemplo `SolicitudPartnerRegistrada` |

| `event_version` | `string` | Sí | Versión del contrato del evento, por ejemplo `v1` |

**### 4.2 Data**

La sección \`data\` contiene la información propia del negocio asociada a la solicitud del partner registrada.

\| Campo | Tipo Avro propuesto | Obligatorio | Significado |

\| --- | --- | --- | --- |

\| \`solicitud\_id\` | \`string\` | Sí | Identificador de la solicitud del partner |

\| \`partner\_id\` | \`string\` | Sí | Identificador del partner |

\| \`referencia\_externa\` | \`string\` | Sí | Referencia externa asociada a la solicitud |

\| \`tipo\_servicio\` | \`string\` | Sí | Tipo de servicio solicitado |

**### 4.3 Decisión sobre timestamps**

Se recomienda representar \`event\_time\` con un tipo temporal compatible con Avro, preferiblemente un valor de tiempo en milisegundos o un timestamp lógico adecuado al sistema.

La razón es que permite:

- trazabilidad temporal del hecho de negocio;

- ordenamiento cronológico del evento de dominio;

- interoperabilidad con consumidores que necesitan distinguir el momento de ocurrencia del hecho de negocio del momento de publicación del mensaje en el broker.

La fecha de ocurrencia del hecho de negocio es conceptualmente diferente de la fecha de publicación del mensaje en el broker.

La decisión concreta puede ajustarse según la implementación de la infraestructura, pero la intención es mantener un campo temporal explícito y uniforme.

**## 5. Schema V1 conceptual**

A continuación se muestra un ejemplo documental del schema Avro para `SolicitudPartnerRegistrada` con `event_version = v1`.

\`\`\`json

{

  "type": "record",

  "name": "SolicitudPartnerRegistrada",

  "namespace": "gestion\_atencion.eventos",

  "fields": [

    {

      "name": "metadata",

      "type": {

        "type": "record",

        "name": "Metadata",

        "fields": [

          { "name": "event\_id", "type": "string" },

          { "name": "event\_time", "type": "long" },

          { "name": "event\_type", "type": "string" },

          { "name": "event\_version", "type": "string" }

        ]

      }

    },

    {

      "name": "data",

      "type": {

        "type": "record",

        "name": "SolicitudPartnerRegistradaData",

        "fields": [

          { "name": "solicitud\_id", "type": "string" },

          { "name": "partner\_id", "type": "string" },

          { "name": "referencia\_externa", "type": "string" },

          { "name": "tipo\_servicio", "type": "string" }

        ]

      }

    }

  ]

}

\`\`\`

Este es un ejemplo documental, no un archivo \`.avsc\` ni una implementación de código.

**## 6. Evolución V1 → V2**

**### 6.1 V1 actual**

El esquema base define:

\`\`\`text

data:

\- solicitud\_id

\- partner\_id

\- referencia\_externa

\- tipo\_servicio

\`\`\`

**### 6.2 V2 propuesto**

El esquema V2 podría añadir:

\`\`\`text

data:

\- solicitud\_id

\- partner\_id

\- referencia\_externa

\- tipo\_servicio

\- estado

\`\`\`

**### 6.3 Compatibilidad con consumidores V1**

El campo `estado` de V2 será opcional o tendrá un valor por defecto compatible.

La estrategia conceptual es:

- agregar el campo `estado` en V2;

- marcarlo como opcional o con default apropiado;

- mantener todos los campos existentes sin cambios de nombre ni significado;

- garantizar que consumidores V1 puedan ignorar el campo nuevo sin romper su lectura.

La intención es que la evolución sea compatible con consumidores más antiguos y que no se rompa la compatibilidad del contrato con versiones previas.

La versión V2 no debe eliminar ni cambiar el significado de `solicitud_id`, `partner_id`, `referencia_externa` ni `tipo_servicio`.

Posteriormente esto se materializará explícitamente en el schema Avro y en la configuración de compatibilidad del Schema Registry.

**## 7. Compatibilidad de schemas**

\| Cambio | Compatibilidad | Explicación |

\| --- | --- | --- |

\| Agregar campo opcional con default | Compatible | Los consumidores antiguos ignoran el nuevo campo si no lo necesitan |

\| Eliminar campo | No compatible | Cambia la estructura esperada por consumidores actuales |

\| Cambiar tipo | No compatible | Puede romper deserialización y validación |

\| Cambiar significado | No compatible | El campo deja de representar lo mismo |

\| Cambiar campo obligatorio a opcional | Puede ser compatible | Depende de las reglas de compatibilidad configuradas y de cómo se defina el schema. |

\| Cambiar campo opcional a obligatorio | No compatible | Requiere que los productores envíen información que no siempre existe |

\| Nueva versión compatible | Compatible si se preserva el contrato base | Permite evolución controlada y legible |

Estas reglas serán configuradas y verificadas posteriormente en Pulsar Schema Registry. En este bloque no se afirma que la configuración del Registry ya esté activa ni operativa.

**## 8. Versionado**

El proyecto debe mantener un esquema claro de versiones para evitar ambigüedad.

**### 8.1 \`event\_type\`**

\`event\_type\` identifica qué tipo de evento es.

Ejemplo:

\- \`SolicitudPartnerRegistrada\`

**### 8.2 \`event\_version\`**

\`event\_version\` identifica la versión del contrato del evento.

Ejemplo:

\- \`v1\`

**### 8.3 Relación con Avro y Pulsar Schema Registry**

La decisión conceptual queda así:

- `event_type` identifica qué tipo de evento es;

- `event_version` identifica la versión del contrato;

- Avro representa técnicamente la estructura del contrato;

- Pulsar Schema Registry administra la evolución y compatibilidad del schema.

No existe un tercer mecanismo independiente de versionado. La versión del evento y la evolución del schema se resuelven de forma consistente a través del contrato y de la gestión de compatibilidad del schema.

**## 9. Relación con Pulsar**

El flujo objetivo de integración es:

\`\`\`text

Producer

   ↓

Avro Schema

   ↓

Pulsar Topic

   ↓

Consumer

   ↓

Avro Deserialization

   ↓

Application

\`\`\`

Esto todavía no se implementa.

La intención aquí es solo dejar definido cómo se representará el contrato y cómo se integrará con el broker futuro.

**## 10. Trade-offs**

**### Ventajas**

\- contrato explícito;

\- tipado fuerte;

\- evolución controlada;

\- integración natural con Pulsar;

\- evita depender de estructuras internas de Python;

\- mejora la claridad del contrato entre microservicios.

**### Costos**

\- requiere administrar schemas;

\- mayor complejidad que un JSON sin esquema;

\- requiere pruebas de compatibilidad;

\- los consumidores deben respetar el contrato definido.

**## 11. Relación con Entrega 4**

Esta decisión técnica ayuda a cumplir el objetivo de Entrega 4 porque fortalece:

\- definición de esquemas de eventos;

\- evolución de contratos;

\- compatibilidad entre versiones;

\- integración mediante eventos;

\- desacoplamiento entre microservicios.

Esto permite dejar una base clara para la siguiente etapa de implementación, sin aún introducir la infraestructura real.

**## 12. Fuera de alcance**

En este bloque no se implementa:

\- producer;

\- consumer;

\- Apache Pulsar real;

\- Schema Registry real;

\- DLQ;

\- retries;

\- idempotencia por \`event\_id\`;

\- deployment ni infraestructura operativa.

**## 13. Decisión final**

Se concluye que:

- `event_type = SolicitudPartnerRegistrada`;

- `event_version = v1`;

\- Avro será el formato de serialización del Integration Event;

\- Pulsar será el broker futuro;

\- Pulsar Schema Registry será el mecanismo de gestión del schema;

\- \`V1\` definirá el contrato mínimo requerido;

\- \`V2\` agregará \`estado\` de forma compatible;

\- la implementación técnica completa se realizará en el siguiente bloque.

La intención de este documento es establecer la base del contrato de integración sin implementar código ni infraestructura real.

**## Resultado**

Se creó el documento:

\- \`docs/06-schema-avro-y-evolucion.md\`

Este archivo describe el esquema Avro conceptual del Integration Event `SolicitudPartnerRegistrada` con `event_version = v1`, su evolución posible hacia V2 y la relación con Pulsar, sin implementar código ni infraestructura adicional.

En este bloque se materializaron además los schemas Avro reales bajo:

\- `src/gestion_atencion/modulos/atencion/infraestructura/contratos/avro/v1/SolicitudPartnerRegistrada.v1.avsc`

\- `src/gestion_atencion/modulos/atencion/infraestructura/contratos/avro/v2/SolicitudPartnerRegistrada.v2.avsc`

Se validaron estructuralmente y quedan disponibles como contrato serializable del evento, sin avanzar en Pulsar, producer, consumer ni Schema Registry.

No se implementó:

\- producer;

\- consumer;

\- Pulsar;

\- Schema Registry;

\- infraestructura del broker.