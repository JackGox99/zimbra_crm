"""
Schemas Pydantic para INTERACCION_MARKETING.

El peso_scoring debe ser >= 0 (replicando el CHECK del DDL). La acción
queda libre como string para soportar nuevas categorías sin migrar el
esquema, pero los valores típicos están documentados.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InteraccionMarketingBase(BaseModel):
    """Campos comunes de una interacción de marketing."""

    accion: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description=(
            "Ej: 'Apertura Correo', 'Click Enlace', 'Descarga Prueba', "
            "'Registro Formulario', 'Visita Pagina Precios'."
        ),
    )
    fecha_interaccion: datetime
    peso_scoring: int = Field(..., ge=0)
    id_prospecto: int
    id_campana: int


class InteraccionMarketingCreate(InteraccionMarketingBase):
    """Payload para POST /api/interacciones."""


class InteraccionMarketingUpdate(BaseModel):
    """Payload para PUT /api/interacciones/{id}."""

    accion: str | None = Field(default=None, min_length=1, max_length=80)
    fecha_interaccion: datetime | None = None
    peso_scoring: int | None = Field(default=None, ge=0)
    id_prospecto: int | None = None
    id_campana: int | None = None


class InteraccionMarketingOut(InteraccionMarketingBase):
    """Respuesta serializada desde el ORM."""

    id_interaccion: int

    model_config = ConfigDict(from_attributes=True)


# --- Schema auxiliar del endpoint transaccional ------------------------
class RegistrarInteraccionOut(BaseModel):
    """
    Resultado del endpoint POST /api/interacciones/registrar.

    Refleja el efecto completo de la transacción:
      * La interacción registrada (con su id autogenerado).
      * La puntuación final del prospecto tras sumar el peso_scoring.
      * Si el prospecto fue promovido a 'Calificado' en esta operación
        (porque la nueva puntuación cruzó el umbral).
    """

    interaccion: InteraccionMarketingOut
    puntuacion_actualizada: int = Field(..., ge=0)
    prospecto_calificado_ahora: bool
    mensaje: str
