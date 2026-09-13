from __future__ import annotations

from typing import Protocol

from gestion_atencion.modulos.atencion.dominio.entidades import Atencion


class RepositorioAtenciones(Protocol):
    def guardar(self, atencion: Atencion) -> None: ...

    def actualizar(self, atencion: Atencion) -> None: ...

    def buscar_por_solicitud_id(self, solicitud_id: str) -> Atencion | None: ...
