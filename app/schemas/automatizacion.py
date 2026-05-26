"""
Schemas Pydantic para los endpoints de automatización (Sesión 3).

Modelan las respuestas de:
  * sp_reporte_mensual_ventas
  * sp_extender_trial
  * sp_marcar_trials_vencidos
  * fn_nivel_interes / fn_dias_restantes_trial / fn_lifetime_value
  * Listado de la bitácora de cambios de estado de prospecto, que se
    almacena en la tabla REPORTE con tipo_reporte='Auditoria Estado
    Prospecto' y `resultado` en formato JSON poblado por el trigger
    `trg_audit_estado_prospecto`.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ----- Reporte mensual (SP) -----------------------------------------------
class ReporteMensualIn(BaseModel):
    anio: int = Field(..., ge=2020, le=2099)
    mes: int = Field(..., ge=1, le=12)


class ReporteMensualOut(BaseModel):
    id_reporte: int
    periodo_inicio: date
    periodo_fin: date
    total_facturado: Decimal
    num_ventas: int
    top_campana: str | None
    resumen: str


# ----- Extender trial (SP) ------------------------------------------------
class ExtenderTrialOut(BaseModel):
    id_prospecto: int
    nombre: str
    fecha_anterior: date
    fecha_nueva: date
    dias_extendidos: int


# ----- Limpieza de trials vencidos (SP) -----------------------------------
class LimpiezaTrialsOut(BaseModel):
    prospectos_marcados: int
    fecha_proceso: date


# ----- Funciones UDF ------------------------------------------------------
class NivelInteresOut(BaseModel):
    puntuacion: int
    nivel_interes: str


class DiasRestantesTrialOut(BaseModel):
    id_prospecto: int
    dias_restantes: int | None
    fecha_fin_prueba: date | None


class LifetimeValueOut(BaseModel):
    id_cliente: int
    lifetime_value: Decimal


# ----- Auditoría (leído de REPORTE) ---------------------------------------
class AuditoriaEventoOut(BaseModel):
    """
    Una entrada de la bitácora de auditoría. Se construye en el router
    leyendo filas de REPORTE con tipo_reporte = 'Auditoria Estado
    Prospecto' y parseando el JSON del campo `resultado`.
    """

    id_reporte: int
    fecha_evento: datetime
    id_prospecto: int
    estado_anterior: str | None
    estado_nuevo: str
    puntuacion: int | None