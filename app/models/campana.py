"""
Modelo CAMPANA.

Representa una campaña de marketing ejecutada por Zimbra (Email, Webinar,
Banner Web, Descarga Trial, Eventos, etc.). Un prospecto, una interacción,
una comunicación enviada y un reporte pueden referenciar a una campaña.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.comunicacion_enviada import ComunicacionEnviada
    from app.models.interaccion_marketing import InteraccionMarketing
    from app.models.prospecto import Prospecto
    from app.models.reporte import Reporte


class Campana(Base):
    """Campaña de marketing ejecutada por Zimbra."""

    __tablename__ = "CAMPANA"
    __table_args__ = (
        CheckConstraint("fecha_fin >= fecha_inicio", name="ck_campana_fechas"),
        CheckConstraint("presupuesto >= 0", name="ck_campana_presupuesto"),
    )

    id_campana: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    # Ej: 'Email', 'Banner Web', 'Webinar', 'Descarga Trial'
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    # Ej: 'Web', 'Email', 'Redes Sociales', 'Eventos'
    canal: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    presupuesto: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    # Posibles: 'Planeada', 'Activa', 'Finalizada', 'Cancelada'
    estado: Mapped[str] = mapped_column(String(30), nullable=False)

    # --- Relaciones inversas ------------------------------------------
    prospectos: Mapped[list["Prospecto"]] = relationship(
        "Prospecto", back_populates="campana_origen"
    )
    interacciones: Mapped[list["InteraccionMarketing"]] = relationship(
        "InteraccionMarketing", back_populates="campana"
    )
    comunicaciones: Mapped[list["ComunicacionEnviada"]] = relationship(
        "ComunicacionEnviada", back_populates="campana"
    )
    reportes: Mapped[list["Reporte"]] = relationship(
        "Reporte", back_populates="campana"
    )

    def __repr__(self) -> str:
        return f"<Campana id={self.id_campana} nombre={self.nombre!r} estado={self.estado!r}>"
