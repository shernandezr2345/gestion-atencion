# Gestión de Atención

Microservicio del bounded context de Gestión de Atención para Hogar de los Alpes.

## Responsabilidad principal

Este microservicio se encarga de transformar una solicitud ya registrada en una atención operativa dentro del negocio.

Actualmente mantiene únicamente el núcleo del dominio, con el Aggregate Root `Atencion` y sus Value Objects mínimos.

## Aggregate Root

- `Atencion`

## Estados principales

- `PENDIENTE`
- `EN_ATENCION`
- `CERRADA`

## Estado actual

La implementación actual contiene solo el dominio de Gestión de Atención, con sus reglas de transición y validaciones internas.

No incluye todavía:
- infraestructura de persistencia
- mensajería
- API REST
- consumidores/productores
- Apache Pulsar
- Avro
- Outbox
- idempotencia

Estos componentes se implementarán en etapas posteriores, una vez estabilizada la estructura del microservicio.
