"""
Schemas Pydantic para PROPUESTA.

valor_estimado >= 0 (CHECK del DDL) y estados restringidos al conjunto
permitido. El servicio de cierre de venta lee/actualiza propuestas en
una transacción ACID — ver `app.services.venta_service`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoPropuesta = Literal["Pendiente", "Aceptada", "Rechazada", "Vencida"]


class PropuestaBase(BaseModel):
    """Campos comunes de una propuesta comercial."""

    descripcion: str = Field(..., min_length=1)
    fecha_propuesta: date
    estado: EstadoPropuesta
    valor_estimado: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    id_prospecto: int


class PropuestaCreate(PropuestaBase):
    """Payload para POST /api/propuestas."""


class PropuestaUpdate(BaseModel):
    """Payload para PUT /api/propuestas/{id}."""

    descripcion: str | None = Field(default=None, min_length=1)
    fecha_propuesta: date | None = None
    estado: EstadoPropuesta | None = None
    valor_estimado: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    id_prospecto: int | None = None


class PropuestaOut(PropuestaBase):
    """Respuesta serializada desde el ORM."""

    id_propuesta: int

    model_config = ConfigDict(from_attributes=True)
