# Gestión de Atención

## 1. Visión general

Este microservicio corresponde al bounded context de Gestión de Atención dentro del dominio de Hogar de los Alpes.

Su responsabilidad principal es representar la transición de una solicitud registrada a una atención operativa del negocio, manteniendo el modelo de dominio mínimo necesario para la gestión del ciclo de vida de la atención.

## 2. Alcance del microservicio

El alcance actual del proyecto está centrado en el dominio y en la lógica de negocio de la atención. 

Se incluye únicamente lo necesario para modelar y validar el ciclo de vida de una atención:

- Aggregate Root: `Atencion`
- Value Objects:
  - `SolicitudId`
  - `PartnerId`
  - `ReferenciaExterna`
  - `TipoServicio`
  - `EstadoAtencion`

## 3. Modelo de dominio mínimo

### Aggregate Root

`Atencion` es la entidad raíz del agregado. Su responsabilidad es controlar el estado de la atención y aplicar las reglas de transición permitidas.

### Value Objects

Los objetos de valor representan datos inmutables y validados:

- `SolicitudId`: identifica la solicitud de atención.
- `PartnerId`: identifica al socio o partner asociado.
- `ReferenciaExterna`: referencia externa de origen o integración.
- `TipoServicio`: tipo de servicio asociado a la atención.
- `EstadoAtencion`: representa el estado actual de la atención.

## 4. Estados de la atención

Los estados definidos para el dominio son:

- `PENDIENTE`
- `EN_ATENCION`
- `CERRADA`

Las transiciones permitidas son las siguientes:

- `PENDIENTE -> EN_ATENCION`
- `EN_ATENCION -> CERRADA`

No se permiten transiciones fuera de este flujo. La validación se realiza dentro del agregado para preservar la integridad del dominio.

## 5. Reglas de negocio del dominio

El modelo debe mantener las siguientes reglas:

- una atención debe crearse con una solicitud válida
- una atención debe estar asociada a un partner válido
- una atención debe contar con una referencia externa válida
- el tipo de servicio debe ser válido
- el estado debe ser consistente con las transiciones permitidas
- no se agregan campos de negocio adicionales fuera del modelo mínimo definido
- no se incorpora lógica no especificada en el dominio

## 6. Estructura del proyecto

La estructura del microservicio sigue la convención de bounded context observada en el repositorio base del proyecto:

```text
gestion-atencion/
├── README.md
├── docs/
├── pyproject.toml
├── src/
│   └── gestion_atencion/
│       ├── __init__.py
│       ├── api/
│       ├── config/
│       ├── modulos/
│       │   └── atencion/
│       │       ├── dominio/
│       │       ├── aplicacion/
│       │       └── infraestructura/
│       └── seedwork/
├── tests/
│   └── unitarias/
└── .gitignore
```

## 7. Fuera de alcance actual

La implementación actual no incluye aún:

- persistencia relacional
- aplicación de base de datos
- publicación de eventos
- consumidores/productores de mensajería
- Pulsar
- Avro
- outbox
- API REST
- integración con infraestructura externa

Estos elementos quedan para fases posteriores, cuando la estructura del microservicio y el dominio base estén estabilizados.

## 8. Estado actual del proyecto

Este documento representa la documentación inicial del microservicio y refleja el estado actual del dominio mínimo validado para Gestión de Atención.

La intención principal del proyecto en esta etapa es mantener un modelo de dominio limpio, coherente y alineado con la arquitectura del contexto bounded.

## 9. Objetivo de la etapa actual

La etapa actual tiene como objetivo:

1. dejar la estructura del microservicio alineada con la convención real del proyecto
2. mantener el agregado `Atencion` y sus value objects mínimos
3. respetar las reglas de dominio sin ampliaciones ni sobreingeniería
4. preparar la base para etapas futuras de aplicación e infraestructura

## 10. Conclusión

Gestión de Atención es un microservicio de dominio pequeño pero estructuralmente importante dentro del sistema. Su valor actual reside en la correcta modelación del agregado `Atencion`, en la preservación de las reglas de transición y en la calidad de la base técnica sobre la que se construirá la siguiente capa.
