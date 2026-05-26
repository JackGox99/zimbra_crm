"""
Schemas Pydantic para PROSPECTO.

Valida correos con EmailStr, controla la puntuación >= 0 y restringe
los estados al conjunto definido en el modelo de dominio.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EstadoProspecto = Literal[
    "Pendiente", "Contactado", "Calificado", "Inadecuado", "Convertido"
]


class ProspectoBase(BaseModel):
    """Campos comunes de un prospecto."""

    nombre: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr
    empresa: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    puntuacion: int = Field(default=0, ge=0)
    estado: EstadoProspecto
    fecha_registro: date
    fecha_inicio_prueba: date | None = None
    fecha_fin_prueba: date | None = None
    id_campana_origen: int | None = None


class ProspectoCreate(ProspectoBase):
    """Payload para POST /api/prospectos."""


class ProspectoUpdate(BaseModel):
    """Payload para PUT /api/prospectos/{id}."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    correo: EmailStr | None = None
    empresa: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    puntuacion: int | None = Field(default=None, ge=0)
    estado: EstadoProspecto | None = None
    fecha_registro: date | None = None
    fecha_inicio_prueba: date | None = None
    fecha_fin_prueba: date | None = None
    id_campana_origen: int | None = None


class ProspectoOut(ProspectoBase):
    """Respuesta serializada desde el ORM."""

    id_prospecto: int

    model_config = ConfigDict(from_attributes=True)
