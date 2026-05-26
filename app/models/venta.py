"""
Modelo VENTA.

Transacción comercial cerrada. Se crea dentro del flujo transaccional
`cerrar_venta` que combina varios SAVEPOINTs (ver
`app.services.venta_service`). Una venta proviene de exactamente una
propuesta aceptada (UNIQUE sobre id_propuesta) y pertenece a un
cliente.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.cliente import Cliente
    from app.models.propuesta import Propuesta


class Venta(Base):
    """Venta cerrada — generada a partir de una propuesta aceptada."""

    __tablename__ = "VENTA"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_venta_monto"),
    )

    id_venta: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    fecha_venta: Mapped[date] = mapped_column(Date, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Posibles: 'Pagada', 'Pendiente', 'Anulada'
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    # Ej: 'Tarjeta', 'Transferencia', 'PayPal'
    metodo_pago: Mapped[str | None] = mapped_column(String(40), nullable=True)
    id_propuesta: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("PROPUESTA.id_propuesta"),
        unique=True,
        nullable=False,
    )
    id_cliente: Mapped[int] = mapped_column(
        Integer, ForeignKey("CLIENTE.id_cliente"), nullable=False
    )

    # --- Relaciones ----------------------------------------------------
    propuesta: Mapped["Propuesta"] = relationship(
        "Propuesta", back_populates="venta"
    )
    cliente: Mapped["Cliente"] = relationship(
        "Cliente", back_populates="ventas"
    )

    def __repr__(self) -> str:
        return (
            f"<Venta id={self.id_venta} monto={self.monto} "
            f"estado={self.estado!r}>"
        )
