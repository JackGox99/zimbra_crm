"""
Modelo COMUNICACION_ENVIADA.

Registro de cada envío individual realizado a un prospecto usando una
plantilla. Permite auditar qué se envió, a quién, con qué plantilla y
qué resultado tuvo (Enviado / Fallido / Rebotado / Abierto).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.campana import Campana
    from app.models.plantilla_comunicacion import PlantillaComunicacion
    from app.models.prospecto import Prospecto


class ComunicacionEnviada(Base):
    """Envío automatizado a un prospecto basado en una plantilla."""

    __tablename__ = "COMUNICACION_ENVIADA"

    id_comunicacion: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    fecha_envio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Posibles: 'Enviado', 'Fallido', 'Rebotado', 'Abierto'
    estado_envio: Mapped[str] = mapped_column(String(30), nullable=False)
    id_plantilla: Mapped[int] = mapped_column(
        Integer, ForeignKey("PLANTILLA_COMUNICACION.id_plantilla"), nullable=False
    )
    id_prospecto: Mapped[int] = mapped_column(
        Integer, ForeignKey("PROSPECTO.id_prospecto"), nullable=False
    )
    id_campana: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("CAMPANA.id_campana"), nullable=True
    )

    # --- Relaciones ----------------------------------------------------
    plantilla: Mapped["PlantillaComunicacion"] = relationship(
        "PlantillaComunicacion", back_populates="comunicaciones"
    )
    prospecto: Mapped["Prospecto"] = relationship(
        "Prospecto", back_populates="comunicaciones"
    )
    campana: Mapped["Campana | None"] = relationship(
        "Campana", back_populates="comunicaciones"
    )

    def __repr__(self) -> str:
        return (
            f"<ComunicacionEnviada id={self.id_comunicacion} "
            f"estado={self.estado_envio!r}>"
        )
