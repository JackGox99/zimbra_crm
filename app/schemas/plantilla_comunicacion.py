"""
Schemas Pydantic para PLANTILLA_COMUNICACION.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoPlantilla = Literal["Email", "SMS", "Notificacion"]


class PlantillaComunicacionBase(BaseModel):
    """Campos comunes de una plantilla de comunicación."""

    nombre: str = Field(..., min_length=1, max_length=100)
    asunto: str = Field(..., min_length=1, max_length=150)
    cuerpo: str = Field(..., min_length=1)
    tipo: TipoPlantilla
    fecha_creacion: date
    activa: bool


class PlantillaComunicacionCreate(PlantillaComunicacionBase):
    """Payload para POST /api/plantillas."""


class PlantillaComunicacionUpdate(BaseModel):
    """Payload para PUT /api/plantillas/{id}."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    asunto: str | None = Field(default=None, min_length=1, max_length=150)
    cuerpo: str | None = Field(default=None, min_length=1)
    tipo: TipoPlantilla | None = None
    fecha_creacion: date | None = None
    activa: bool | None = None


class PlantillaComunicacionOut(PlantillaComunicacionBase):
    """Respuesta serializada desde el ORM."""

    id_plantilla: int

    model_config = ConfigDict(from_attributes=True)
