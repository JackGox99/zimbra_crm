"""
Modelo PROSPECTO.

Representa un visitante interesado en Zimbra que aún no es cliente.
La puntuación se incrementa según las interacciones de marketing que
realiza (apertura de correos, clics, visita a página de precios,
descarga de trial, etc.). Cuando supera el umbral configurado, el
estado pasa a 'Calificado'.

El periodo de prueba de 60 días se controla con `fecha_inicio_prueba`
y `fecha_fin_prueba`.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.campana import Campana
    from app.models.cliente import Cliente
    from app.models.comunicacion_enviada import ComunicacionEnviada
    from app.models.interaccion_marketing import InteraccionMarketing
    from app.models.propuesta import Propuesta


class Prospecto(Base):
    """Visitante interesado todavía no convertido a cliente."""

    __tablename__ = "PROSPECTO"
    __table_args__ = (
        CheckConstraint("puntuacion >= 0", name="ck_prospecto_puntuacion"),
    )

    id_prospecto: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    empresa: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    puntuacion: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    # Posibles: 'Pendiente', 'Contactado', 'Calificado', 'Inadecuado', 'Convertido'
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    fecha_registro: Mapped[date] = mapped_column(Date, nullable=False)
    # Ventana de 60 días de prueba del ZCS.
    fecha_inicio_prueba: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin_prueba: Mapped[date | None] = mapped_column(Date, nullable=True)
    id_campana_origen: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("CAMPANA.id_campana"), nullable=True
    )

    # --- Relaciones ----------------------------------------------------
    campana_origen: Mapped["Campana | None"] = relationship(
        "Campana", back_populates="prospectos"
    )
    interacciones: Mapped[list["InteraccionMarketing"]] = relationship(
        "InteraccionMarketing", back_populates="prospecto"
    )
    comunicaciones: Mapped[list["ComunicacionEnviada"]] = relationship(
        "ComunicacionEnviada", back_populates="prospecto"
    )
    propuestas: Mapped[list["Propuesta"]] = relationship(
        "Propuesta", back_populates="prospecto"
    )
    cliente: Mapped["Cliente | None"] = relationship(
        "Cliente", back_populates="prospecto", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<Prospecto id={self.id_prospecto} correo={self.correo!r} "
            f"estado={self.estado!r} puntuacion={self.puntuacion}>"
        )
