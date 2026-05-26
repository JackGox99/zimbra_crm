"""
Schemas Pydantic para COMUNICACION_ENVIADA.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoEnvio = Literal["Enviado", "Fallido", "Rebotado", "Abierto"]


class ComunicacionEnviadaBase(BaseModel):
    """Campos comunes de un envío de comunicación."""

    fecha_envio: datetime
    estado_envio: EstadoEnvio
    id_plantilla: int
    id_prospecto: int
    id_campana: int | None = None


class ComunicacionEnviadaCreate(ComunicacionEnviadaBase):
    """Payload para POST /api/comunicaciones."""


class ComunicacionEnviadaUpdate(BaseModel):
    """Payload para PUT /api/comunicaciones/{id}."""

    fecha_envio: datetime | None = None
    estado_envio: EstadoEnvio | None = None
    id_plantilla: int | None = None
    id_prospecto: int | None = None
    id_campana: int | None = None


class ComunicacionEnviadaOut(ComunicacionEnviadaBase):
    """Respuesta serializada desde el ORM."""

    id_comunicacion: int

    model_config = ConfigDict(from_attributes=True)
