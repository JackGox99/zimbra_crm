"""
Modelo PROPUESTA.

Oferta comercial generada a un prospecto. La propuesta puede estar
Pendiente, ser Aceptada (lo que dispara el cierre de venta dentro de
una transacción ACID), Rechazada o Vencer por tiempo.

Tiene una relación 1:1 con VENTA: una propuesta aceptada produce
exactamente una venta (UNIQUE sobre VENTA.id_propuesta).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.prospecto import Prospecto
    from app.models.venta import Venta


class Propuesta(Base):
    """Oferta comercial dirigida a un prospecto."""

    __tablename__ = "PROPUESTA"
    __table_args__ = (
        CheckConstraint("valor_estimado >= 0", name="ck_propuesta_valor"),
    )

    id_propuesta: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_propuesta: Mapped[date] = mapped_column(Date, nullable=False)
    # Posibles: 'Pendiente', 'Aceptada', 'Rechazada', 'Vencida'
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    valor_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    id_prospecto: Mapped[int] = mapped_column(
        Integer, ForeignKey("PROSPECTO.id_prospecto"), nullable=False
    )

    # --- Relaciones ----------------------------------------------------
    prospecto: Mapped["Prospecto"] = relationship(
        "Prospecto", back_populates="propuestas"
    )
    # 1:1 forzado por UNIQUE en VENTA.id_propuesta
    venta: Mapped["Venta | None"] = relationship(
        "Venta", back_populates="propuesta", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<Propuesta id={self.id_propuesta} estado={self.estado!r} "
            f"valor={self.valor_estimado}>"
        )
