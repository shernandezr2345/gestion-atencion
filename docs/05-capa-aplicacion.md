# Capa de aplicación de Gestión de Atención

## 1. Objetivo

La capa de aplicación coordina los casos de uso del bounded context de Gestión de Atención y actúa como intermediaria entre las entradas externas, el dominio y la persistencia.

Su responsabilidad principal es orquestar el flujo de ejecución del caso de uso sin contener reglas de negocio propias del agregado.

El flujo esperado es:

```text
Entrada
   ↓
Application
   ↓
Domain
   ↓
Repository
```

La Application no debe contener reglas de negocio propias del agregado. Es decir, no debe decidir si una transición de estado es válida ni definir invariantes del dominio. Esa lógica debe permanecer en `Atencion` y en sus Value Objects.

## 2. Casos de uso

### 2.1 Crear Atención

Responsabilidad:

- recibir los datos necesarios para crear una Atención;
- verificar si ya existe una atención para `solicitud_id`;
- crear el agregado mediante el dominio;
- persistir mediante `Repository`.

Datos de entrada:

- `solicitud_id`
- `partner_id`
- `referencia_externa`
- `tipo_servicio`

La aplicación debe coordinar esta secuencia:

1. validar que la entrada sea suficiente para crear el agregado;
2. consultar si ya existe una atención para la misma `solicitud_id`;
3. si no existe, invocar `Atencion.crear(...)`;
4. persistir el resultado con `Repository.guardar(...)`.

Esto corresponde al caso de uso de creación del agregado y no incorpora lógica operativa del dominio.

### 2.2 Cambiar Estado de Atención

Responsabilidad:

- obtener la Atención existente;
- solicitar al dominio el cambio de estado;
- persistir el agregado actualizado.

Estados:

- `PENDIENTE`
- `EN_ATENCION`
- `CERRADA`

Transiciones permitidas:

- `PENDIENTE -> EN_ATENCION`
- `EN_ATENCION -> CERRADA`

La aplicación no decide si una transición es válida. Esa decisión pertenece al dominio. La aplicación solo orquesta la llamada al método correspondiente de `Atencion` y luego delega la persistencia al `Repository`.

## 3. Flujo de Crear Atención

El flujo de creación debe ser:

```text
SolicitudPartnerRegistrada.v1
        ↓
Application
        ↓
buscar_por_solicitud_id()
        ↓
¿Existe?
   ├── Sí → tratar como procesamiento idempotente
   └── No
        ↓
crear Atencion
        ↓
Repository.guardar()
        ↓
resultado
```

### Idempotencia inicial

En esta etapa, la idempotencia se basa en `solicitud_id`.

La idea es que una misma solicitud no se procese dos veces dentro del bounded context. El caso de uso debe comprobar si ya existe una atención para la misma `solicitud_id` antes de crear un nuevo agregado.

La deduplicación por `event_id` queda fuera de este alcance y se considera una etapa posterior.

## 4. Flujo de cambio de estado

El flujo de cambio de estado debe ser:

```text
Solicitud de cambio
        ↓
Application
        ↓
Repository.buscar(...)
        ↓
Atencion
        ↓
metodo del dominio
        ↓
validación de transición
        ↓
Repository.actualizar()
        ↓
resultado
```

### Regla de diseño

La Application no debe decidir si la transición es válida. Ese criterio debe estar encapsulado en el agregado `Atencion`, ya sea en el método de cambio de estado o en la validación interna de transiciones.

La Application solo debe:

- cargar la entidad correcta;
- invocar el método del dominio;
- persistir la nueva versión del agregado mediante `Repository.actualizar()`.

## 5. Responsabilidades por capa

| Capa | Responsabilidad |
| --- | --- |
| Dominio | reglas de negocio, invariantes, estados, transiciones, agregado `Atencion`, Value Objects |
| Application | casos de uso, orquestación, coordinación, uso del `Repository`, manejo del flujo de aplicación |
| Infrastructure | PostgreSQL, implementación concreta del `Repository`, detalles técnicos |

### Dominio

La capa de dominio debe mantener:

- reglas de negocio;
- estados y transiciones;
- invariantes del agregado;
- validate de cambios de estado;
- `Atencion` como Aggregate Root;
- Value Objects para identidad y datos del dominio.

### Application

La capa de aplicación debe mantener:

- casos de uso de Gestión de Atención;
- coordinación entre entradas y dominio;
- uso de `Repository` para crear y actualizar registros;
- flujo de aplicación sin lógica de negocio propia del agregado.

### Infrastructure

La infraestructura debe implementar:

- acceso a PostgreSQL;
- `RepositorioAtencionesPostgres`;
- detalles de conexión, SQL y mapeo;
- parte técnica de persistencia.

## 6. Dependencias

La capa de aplicación depende de abstracciones y puertos, no de tecnologías concretas.

La Application depende de:

- el contrato del `Repository`;
- las entidades del dominio;
- los Value Objects y las reglas del agregado.

La Application NO depende directamente de:

- PostgreSQL;
- `psycopg`;
- SQL;
- Pulsar;
- Avro;

Esto se alinea con el principio de Dependency Inversion.

## 7. Manejo de errores

La capa de aplicación debe manejar conceptualmente errores del flujo de aplicación, pero sin resolver reglas del dominio ni de infraestructura.

Los errores esperados incluyen:

- atención no encontrada;
- atención ya existente;
- transición inválida;
- error de persistencia.

### Principio de localización

- Las reglas de negocio y validación de transición deben permanecer en el dominio.
- La duplicidad por `solicitud_id` debe ser tratada por la lógica de aplicación y/o validación previa al guardado.
- El error técnico de persistencia debe ser manejado en la infraestructura y propagado con el nivel adecuado.

No deben usarse excepciones genéricas para ocultar problemas de dominio o de infraestructura.

## 8. Relación con el Integration Event

La Application será posteriormente utilizada por el Consumer de:

- `SolicitudPartnerRegistrada.v1`

Sin embargo, en esta etapa no se implementa el Consumer.

El flujo objetivo será:

```text
Pulsar
   ↓
Consumer
   ↓
Application
   ↓
Domain
   ↓
Repository
   ↓
PostgreSQL
```

Esto implica que la Application debe ser un punto de integración útil para procesar mensajes de dominio y coordinar la reacción del bounded context, pero sin acoplarse a mecanismos de mensajería en este bloque.

## 9. Relación con los atributos de calidad

### 9.1 Resiliencia

La separación entre Consumer, Application, Domain y Repository ayuda a que el procesamiento evento a evento pueda reintentarse sin acoplar directamente el flujo de atención a la base de datos o al dominio.

La capa de aplicación aporta orden y aislamiento a ese flujo, pero no garantiza resiliencia por sí sola.

### 9.2 Escalabilidad

Se podrán ejecutar múltiples instancias del Consumer y de la aplicación sin necesidad de modificar la lógica del agregado ni la estructura de dominio.

La separación de responsabilidades contribuye a una arquitectura que puede escalar de manera más limpia.

### 9.3 Extensibilidad

Los casos de uso pueden evolucionar sin acoplar el dominio a tecnologías de mensajería ni de persistencia.

La estructura favorece cambios incrementales en la capa de aplicación sin reclutar reglas del negocio a tecnologías externas.

## 10. Trade-offs

### Ventajas

- separación clara de responsabilidades;
- dominio independiente de infraestructura;
- facilidad de pruebas;
- facilita integración con eventos;
- facilita evolución del sistema.

### Costos

- más capas;
- más clases e interfaces;
- complejidad inicial mayor.

La aplicación de esta estructura tiene un costo inicial de diseño, pero mejora la mantenibilidad y la claridad del bounded context.

## 11. Fuera de alcance

Durante esta etapa no se incluirá:

- Saga;
- BFF;
- Event Sourcing;
- CQRS completo;
- comandos remotos;
- REST para operaciones entre microservicios;
- lógica de Pulsar;
- Avro;
- DLQ;
- retry policies avanzadas.

## 12. Decisión final

La capa de aplicación será el punto de coordinación entre las entradas externas, el dominio y la persistencia.

Mantendrá la responsabilidad de:

- orquestar casos de uso;
- utilizar el dominio como fuente de reglas;
- delegar almacenamiento en el `Repository`;
- mantener la infraestructura desacoplada mediante abstracciones.

Las reglas de negocio seguirán viviendo en `Atencion` y sus Value Objects. La infraestructura continuará implementando los detalles técnicos de PostgreSQL y almacenamiento.

## Resultado

Se creó el documento:

- `docs/05-capa-aplicacion.md`

Este documento describe el diseño de la capa de aplicación sin implementar código de producción ni modificar los elementos ya validados del dominio y de la persistencia.

No se realizaron cambios en:

- dominio;
- repository;
- infraestructura;
- mensajes/eventos;
- código de implementación.
