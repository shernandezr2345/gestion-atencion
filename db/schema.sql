CREATE TABLE IF NOT EXISTS atenciones (
    id_atencion VARCHAR(36) PRIMARY KEY,
    solicitud_id VARCHAR(255) NOT NULL,
    partner_id VARCHAR(255) NOT NULL,
    referencia_externa VARCHAR(255) NOT NULL,
    tipo_servicio VARCHAR(255) NOT NULL,
    estado VARCHAR(32) NOT NULL CHECK (estado IN ('PENDIENTE', 'EN_ATENCION', 'CERRADA')),
    fecha_creacion TIMESTAMPTZ NOT NULL,
    CONSTRAINT atenciones_solicitud_unica UNIQUE (solicitud_id)
);
