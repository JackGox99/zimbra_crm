"""
Modelo INTERACCION_MARKETING.

Registra cada acción que un prospecto realiza sobre el sitio o sobre
una campaña (apertura de correo, clic en enlace, visita a página de
precios, descarga de la prueba, etc.). Cada interacción aporta un
`peso_scoring` que el servicio de scoring suma a la puntuación del
prospecto dentro de una transacción atómica.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.campana import Campana
    from app.models.prospecto import Prospecto


class InteraccionMarketing(Base):
    """Acción de un prospecto sobre una campaña; alimenta el scoring."""

    __tablename__ = "INTERACCION_MARKETING"
    __table_args__ = (
        CheckConstraint("peso_scoring >= 0", name="ck_interaccion_peso"),
    )

    id_interaccion: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    # Ej: 'Apertura Correo', 'Click Enlace', 'Descarga Prueba',
    #     'Registro Formulario', 'Visita Pagina Precios'
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    fecha_interaccion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    peso_scoring: Mapped[int] = mapped_column(Integer, nullable=False)
    id_prospecto: Mapped[int] = mapped_column(
        Integer, ForeignKey("PROSPECTO.id_prospecto"), nullable=False
    )
    id_campana: Mapped[int] = mapped_column(
        Integer, ForeignKey("CAMPANA.id_campana"), nullable=False
    )

    # --- Relaciones ----------------------------------------------------
    prospecto: Mapped["Prospecto"] = relationship(
        "Prospecto", back_populates="interacciones"
    )
    campana: Mapped["Campana"] = relationship(
        "Campana", back_populates="interacciones"
    )

    def __repr__(self) -> str:
        return (
            f"<InteraccionMarketing id={self.id_interaccion} "
            f"accion={self.accion!r} peso={self.peso_scoring}>"
        )
