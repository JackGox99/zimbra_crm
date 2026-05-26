"""
Modelo REPORTE.

Reporte parametrizado generado sobre el dominio: rendimiento de
campaña, prospectos calificados, ventas del periodo, embudo de
conversión, etc. El campo `resultado` guarda el texto/JSON resultante
de la consulta materializada en el momento de la generación.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.campana import Campana


class Reporte(Base):
    """Reporte parametrizado sobre el dominio (campañas, ventas, conversión)."""

    __tablename__ = "REPORTE"

    id_reporte: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    # Ej: 'Rendimiento Campana', 'Prospectos Calificados',
    #     'Ventas Periodo', 'Conversion Embudo'
    tipo_reporte: Mapped[str] = mapped_column(String(60), nullable=False)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    periodo_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    periodo_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    resultado: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_campana: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("CAMPANA.id_campana"), nullable=True
    )

    # --- Relaciones ----------------------------------------------------
    campana: Mapped["Campana | None"] = relationship(
        "Campana", back_populates="reportes"
    )

    def __repr__(self) -> str:
        return (
            f"<Reporte id={self.id_reporte} tipo={self.tipo_reporte!r}>"
        )
