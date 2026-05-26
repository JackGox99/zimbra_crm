"""
Modelo CLIENTE.

Cliente activo de Zimbra, originado a partir de un PROSPECTO cuyo ciclo
de ventas terminó en una propuesta aceptada. La relación con PROSPECTO
es 1:1 (UNIQUE) y opcional para soportar casos donde el cliente fue
creado por otra vía (importación legacy, demo, etc.).

Los campos `sync_salesforce` y `fecha_ult_sync` simulan la integración
con CRM Salesforce mediante un flag booleano y la marca temporal de la
última sincronización exitosa.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.prospecto import Prospecto
    from app.models.venta import Venta


class Cliente(Base):
    """Cliente activo — prospecto convertido tras una venta cerrada."""

    __tablename__ = "CLIENTE"

    id_cliente: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    empresa: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fecha_registro: Mapped[date] = mapped_column(Date, nullable=False)
    id_prospecto: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("PROSPECTO.id_prospecto"),
        unique=True,
        nullable=True,
    )
    sync_salesforce: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fecha_ult_sync: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # --- Relaciones ----------------------------------------------------
    prospecto: Mapped["Prospecto | None"] = relationship(
        "Prospecto", back_populates="cliente"
    )
    ventas: Mapped[list["Venta"]] = relationship(
        "Venta", back_populates="cliente"
    )

    def __repr__(self) -> str:
        return f"<Cliente id={self.id_cliente} correo={self.correo!r}>"
