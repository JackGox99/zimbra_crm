"""
Schemas Pydantic para REPORTE.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReporteBase(BaseModel):
    """Campos comunes de un reporte parametrizado."""

    tipo_reporte: str = Field(..., min_length=1, max_length=60)
    fecha_generacion: datetime
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    resultado: str | None = None
    id_campana: int | None = None


class ReporteCreate(ReporteBase):
    """Payload para POST /api/reportes."""


class ReporteUpdate(BaseModel):
    """Payload para PUT /api/reportes/{id}."""

    tipo_reporte: str | None = Field(default=None, min_length=1, max_length=60)
    fecha_generacion: datetime | None = None
    periodo_inicio: date | None = None
    periodo_fin: date | None = None
    resultado: str | None = None
    id_campana: int | None = None


class ReporteOut(ReporteBase):
    """Respuesta serializada desde el ORM."""

    id_reporte: int

    model_config = ConfigDict(from_attributes=True)


# --- Schemas auxiliares para los endpoints consultivos -----------------
class EmbudoConversionOut(BaseModel):
    """
    Resultado del endpoint GET /api/reportes/conversion.

    Refleja el embudo clásico de marketing → ventas:
    Prospectos → Activos → Calificados → Clientes → Ventas pagadas.
    """

    total_prospectos: int = Field(..., description="Total de prospectos registrados.")
    total_prospectos_activos: int = Field(
        ..., description="Prospectos con estado distinto de 'Inadecuado'."
    )
    total_calificados: int = Field(
        ..., description="Prospectos con estado 'Calificado' o 'Convertido'."
    )
    total_clientes: int = Field(..., description="Total de clientes registrados.")
    total_ventas_pagadas: int = Field(
        ..., description="Ventas con estado 'Pagada'."
    )
    ingresos_totales: Decimal = Field(
        ..., description="Suma de los montos de ventas con estado 'Pagada'."
    )


class RendimientoCampanaOut(BaseModel):
    """
    Resultado de GET /api/reportes/campanas/{id}/rendimiento.

    Calcula el ROI de una campaña comparando su presupuesto con los
    ingresos efectivamente generados por los prospectos que entraron
    por esa campaña.
    """

    id_campana: int
    nombre_campana: str
    tipo: str
    canal: str
    presupuesto: Decimal | None
    prospectos_generados: int
    prospectos_calificados: int
    clientes_convertidos: int
    ventas_cerradas: int
    ingresos_generados: Decimal
    roi_porcentaje: float | None = Field(
        None,
        description=(
            "(ingresos − presupuesto) / presupuesto × 100. "
            "None si la campaña no tiene presupuesto definido o es cero."
        ),
    )
