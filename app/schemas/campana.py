"""
Schemas Pydantic para CAMPANA.

Valida la entrada y serializa la salida de los endpoints relacionados
con campañas de marketing. Refleja las restricciones del DDL:
  * fecha_fin >= fecha_inicio
  * presupuesto >= 0
  * estado ∈ {Planeada, Activa, Finalizada, Cancelada}
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EstadoCampana = Literal["Planeada", "Activa", "Finalizada", "Cancelada"]


class CampanaBase(BaseModel):
    """Campos comunes de una campaña."""

    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., min_length=1, max_length=50)
    canal: str = Field(..., min_length=1, max_length=50)
    fecha_inicio: date
    fecha_fin: date
    presupuesto: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    estado: EstadoCampana


class CampanaCreate(CampanaBase):
    """Payload para POST /api/campanas."""

    @model_validator(mode="after")
    def _validar_rango_fechas(self) -> "CampanaCreate":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual que fecha_inicio")
        return self


class CampanaUpdate(BaseModel):
    """Payload para PUT /api/campanas/{id} — todos los campos opcionales."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: str | None = Field(default=None, min_length=1, max_length=50)
    canal: str | None = Field(default=None, min_length=1, max_length=50)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    presupuesto: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    estado: EstadoCampana | None = None


class CampanaOut(CampanaBase):
    """Respuesta serializada desde el ORM."""

    id_campana: int

    model_config = ConfigDict(from_attributes=True)
