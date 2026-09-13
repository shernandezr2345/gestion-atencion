# Validación del contrato: SolicitudPartnerRegistrada.v1

## Objetivo

Validar que el diseño del contrato de integración `SolicitudPartnerRegistrada.v1` cumple con el alcance definido para el microservicio de Gestión de Atención y es consistente con el bounded context del proyecto.

Este documento no implementa infraestructura ni código. Su propósito es verificar solo la corrección del diseño del contrato.

## 1. Verificación del alcance

Se revisa que el contrato:

- pertenece al bounded context de Gestión de Atención
- representa un `Integration Event`
- comunica un hecho de negocio entre microservicios
- no depende del modelo interno de dominio de Gestión de Atención
- no exige acceso directo a la base de datos de Solicitudes Partner
- usa información mínima suficiente para crear una atención local

Resultado: cumple con el alcance documental propuesto.

## 2. Verificación del nombre y de la versión

El contrato definido es:

- `SolicitudPartnerRegistrada.v1`

Esto cumple con la regla de versionado del contrato y hace explícita la compatibilidad evolutiva entre versiones futuras.

## 3. Verificación de la estructura

La estructura del mensaje es la siguiente:

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

Se valida que:

- `metadata` contiene la identidad y la versión del evento
- `data` contiene los campos mínimos de integración
- no se agregan campos adicionales en V1
- el evento es un contrato externo y no un modelo interno del productor

## 4. Verificación de los campos

Se valida la presencia de los campos requeridos:

| Campo | Ubicación | Requerido | Observación |
|---|---|---:|---|
| `event_id` | `metadata` | Sí | Identificador único del evento |
| `event_time` | `metadata` | Sí | Momento del hecho de negocio |
| `event_type` | `metadata` | Sí | Nombre y versión del evento |
| `event_version` | `metadata` | Sí | Versión del contrato |
| `solicitud_id` | `data` | Sí | Identificador de la solicitud |
| `partner_id` | `data` | Sí | Identificador del partner |
| `referencia_externa` | `data` | Sí | Referencia externa de la solicitud |
| `tipo_servicio` | `data` | Sí | Tipo de servicio |

Se confirma que el payload mínimo es suficiente para el consumo del microsservicio de Gestión de Atención, sin introducir información que no esté justificada.

## 5. Verificación de la semántica del contrato

Se revisa que el contrato comunica solo lo necesario:

- la solicitud fue registrada
- la acción es observable desde otros bounded contexts
- no se comparten entidades completas ni tablas internas
- no se exponen detalles de implementación del productor
- los consumidores no necesitan saber cómo está modelado internamente Solicitudes Partner

Resultado: consistente con la separación de responsabilidades y con la arquitectura distribuida.

## 6. Verificación de compatibilidad y evolución

Se valida la regla de evolución del contrato:

```text
SolicitudPartnerRegistrada.v2
  -> agrega data.estado
```

Con eso se cumple la idea de compatibilidad en evolución:

- agregar un campo opcional es compatible con consumidores V1
- eliminar o cambiar el significado de campos existentes no es compatible
- nuevas versiones deben mantener la compatibilidad prevista

Esto es una decisión correcta para un Integration Event de tipo de negocio.

## 7. Verificación de reglas del contrato

Las reglas definidas para V1 se cumplen conceptualmente:

- no se elimina ni cambia el significado de un campo existente
- los consumidores no deben conocer el modelo interno del productor
- `solicitud_id` identifica la solicitud de negocio
- `event_id` identifica la instancia del evento
- la versión forma parte del contrato
- el diseño evita incluir elementos ajenos como `estado`, `prioridad` o campos operativos en V1

## 8. Verificación de la relación con Gestión de Atención

El contrato encaja con el flujo objetivo del microservicio:

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

Se valida que este flujo es conceptual y congruente con la intención del bounded context. Esto no implica haber implementado infraestructura ni conexión real con Pulsar.

## 9. Verificación de decisión de diseño

Se confirma que el diseño evita incorporar artefactos no aprobados para esta etapa:

- no hay Avro
- no hay Pulsar real
- no hay consumer implementado
- no hay producer implementado
- no hay cambios en el modelo interno de dominio de Gestión de Atención

Esto mantiene la documentación dentro del alcance solicitado.

## 10. Resultado de la validación

### A. Correcto

El diseño del contrato `SolicitudPartnerRegistrada.v1` es correcto para esta etapa del proyecto, porque:

- comunica un hecho de integración
- es mínimo y estable
- cumple con el principio de desacoplamiento entre microservicios
- permite a Gestión de Atención crear su propio modelo local
- mantiene la propiedad separada de los datos
- está versionado y prepara la evolución compatible

### B. Problemas encontrados

No se encontraron problemas de diseño en el documento del contrato para esta etapa.

### C. Documentación validada

Se validó el contenido del archivo:

- `docs/03-contrato-evento-solicitud-partner-registrada.md`

### D. Archivos involucrados

Archivo validado:

- `docs/03-contrato-evento-solicitud-partner-registrada.md`

No se modificó ningún archivo de código ni de referencia.

### E. Recomendación

El contrato puede avanzar sin cambios en la siguiente etapa documental, siempre manteniendo la misma firma de V1 y sin introducir campos adicionales no aprobados.

Se recomienda mantener este diseño y continuar con la siguiente documentación de persistencia o arquitectura, sin implementar infraestructura ni lógica ejecutable aún.

## Conclusión

El contrato `SolicitudPartnerRegistrada.v1` está bien definido para su propósito de integración entre microservicios, es consistente con el bounded context de Gestión de Atención y mantiene la separación de responsabilidades que exige la arquitectura distribuida del proyecto.
