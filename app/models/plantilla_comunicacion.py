"""
Modelo PLANTILLA_COMUNICACION.

Plantilla reutilizable usada por el sistema para enviar comunicaciones
automáticas a los prospectos (bienvenida al trial, recordatorio de fin
de prueba, ofertas, etc.). Cada envío individual queda registrado en
COMUNICACION_ENVIADA y referencia esta plantilla.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.comunicacion_enviada import ComunicacionEnviada


class PlantillaComunicacion(Base):
    """Plantilla reutilizable de correo / SMS / notificación."""

    __tablename__ = "PLANTILLA_COMUNICACION"

    id_plantilla: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    asunto: Mapped[str] = mapped_column(String(150), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    # Posibles: 'Email', 'SMS', 'Notificacion'
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha_creacion: Mapped[date] = mapped_column(Date, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # --- Relaciones ----------------------------------------------------
    comunicaciones: Mapped[list["ComunicacionEnviada"]] = relationship(
        "ComunicacionEnviada", back_populates="plantilla"
    )

    def __repr__(self) -> str:
        return (
            f"<PlantillaComunicacion id={self.id_plantilla} "
            f"nombre={self.nombre!r} activa={self.activa}>"
        )
