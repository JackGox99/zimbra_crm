"""
Schemas Pydantic para VENTA.

monto > 0 (CHECK estricto del DDL). El endpoint transaccional principal
(`POST /api/ventas/cerrar-venta`) NO usa VentaCreate: arma la venta a
partir de la propuesta aceptada dentro de la transacción ACID. Estos
schemas se usan para CRUD básico y para retornar la venta resultante.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EstadoVenta = Literal["Pagada", "Pendiente", "Anulada"]


class VentaBase(BaseModel):
    """Campos comunes de una venta cerrada."""

    fecha_venta: date
    monto: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    estado: EstadoVenta
    metodo_pago: str | None = Field(default=None, max_length=40)
    id_propuesta: int
    id_cliente: int


class VentaCreate(VentaBase):
    """Payload para POST /api/ventas (creación directa, no transaccional)."""


class VentaUpdate(BaseModel):
    """Payload para PUT /api/ventas/{id}."""

    fecha_venta: date | None = None
    monto: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    estado: EstadoVenta | None = None
    metodo_pago: str | None = Field(default=None, max_length=40)
    id_propuesta: int | None = None
    id_cliente: int | None = None


class VentaOut(VentaBase):
    """Respuesta serializada desde el ORM."""

    id_venta: int

    model_config = ConfigDict(from_attributes=True)


# --- Schemas auxiliares del endpoint transaccional ---------------------
class CerrarVentaIn(BaseModel):
    """Payload mínimo para `POST /api/ventas/cerrar-venta`."""

    id_propuesta: int = Field(..., gt=0)
    metodo_pago: str | None = Field(default="Transferencia", max_length=40)


class CerrarVentaOut(BaseModel):
    """Resultado del cierre de venta con el detalle de la transacción."""

    venta: VentaOut
    cliente_creado: bool = Field(
        ...,
        description=(
            "True si se creó un nuevo cliente; False si ya existía y se "
            "reutilizó (caso recompra)."
        ),
    )
    mensaje: str
