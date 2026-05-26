"""
Router de automatización (Entrega 3).

Expone endpoints que invocan los procedimientos almacenados, funciones
UDF y triggers definidos al final de `sql/zimbra_crm.sql`. Cada endpoint
está mapeado a un caso de negocio real:

  * POST /api/automatizacion/reporte-mensual
        → CALL sp_reporte_mensual_ventas(anio, mes)
        Cierre comercial del mes con totales y top campaña.

  * POST /api/automatizacion/extender-trial/{id_prospecto}?dias=N
        → CALL sp_extender_trial(id, dias)
        El comercial extiende el periodo de prueba de un lead.

  * POST /api/automatizacion/limpiar-trials-vencidos
        → CALL sp_marcar_trials_vencidos()
        Limpieza periódica de leads cuyo trial venció.

  * GET  /api/automatizacion/funciones/nivel-interes?puntuacion=N
        → SELECT fn_nivel_interes(N)
        Etiqueta cualitativa centralizada (sustituye lógica del JS).

  * GET  /api/automatizacion/funciones/dias-restantes/{id_prospecto}
        → SELECT fn_dias_restantes_trial(id)
        Días faltantes para que termine el trial del prospecto.

  * GET  /api/automatizacion/funciones/lifetime-value/{id_cliente}
        → SELECT fn_lifetime_value(id)
        Total facturado al cliente, sumando todas sus ventas pagadas.

  * GET  /api/automatizacion/auditoria
        Lee filas de REPORTE con tipo_reporte='Auditoria Estado
        Prospecto' (poblada por el trigger trg_audit_estado_prospecto)
        y parsea el JSON del campo `resultado`.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reporte import Reporte
from app.schemas.automatizacion import (
    AuditoriaEventoOut,
    DiasRestantesTrialOut,
    ExtenderTrialOut,
    LifetimeValueOut,
    LimpiezaTrialsOut,
    NivelInteresOut,
    ReporteMensualIn,
    ReporteMensualOut,
)

AUDIT_TIPO = "Auditoria Estado Prospecto"

router = APIRouter()


# =====================================================================
#  PROCEDIMIENTOS ALMACENADOS
# =====================================================================
@router.post(
    "/reporte-mensual",
    response_model=ReporteMensualOut,
    summary="Genera reporte mensual de ventas (CALL sp_reporte_mensual_ventas)",
)
def ejecutar_reporte_mensual(
    payload: ReporteMensualIn, db: Session = Depends(get_db)
) -> ReporteMensualOut:
    """
    Invoca el SP que totaliza ventas pagadas del mes, identifica la
    campaña con mayor facturación y persiste el resultado en REPORTE.
    """
    try:
        cursor = db.connection().connection.cursor()
        cursor.callproc("sp_reporte_mensual_ventas", [payload.anio, payload.mes])
        row = cursor.fetchone()
        cursor.close()
        db.commit()
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))

    if row is None:
        raise HTTPException(
            status_code=500,
            detail="El SP no devolvió resultados (verifica que existan ventas en el periodo).",
        )

    return ReporteMensualOut(
        id_reporte=row[0],
        periodo_inicio=row[1],
        periodo_fin=row[2],
        total_facturado=Decimal(str(row[3])),
        num_ventas=int(row[4]),
        top_campana=row[5],
        resumen=row[6],
    )


@router.post(
    "/extender-trial/{id_prospecto}",
    response_model=ExtenderTrialOut,
    summary="Extiende el trial del prospecto (CALL sp_extender_trial)",
)
def ejecutar_extender_trial(
    id_prospecto: int,
    dias: int = Query(..., ge=1, le=90, description="Días a sumar al trial"),
    db: Session = Depends(get_db),
) -> ExtenderTrialOut:
    """
    El SP valida que el prospecto tenga trial activo y que `dias` esté
    en [1, 90]. Lanza SQLSTATE 45000 con mensaje legible si no se
    cumplen las precondiciones.
    """
    try:
        cursor = db.connection().connection.cursor()
        cursor.callproc("sp_extender_trial", [id_prospecto, dias])
        row = cursor.fetchone()
        cursor.close()
        db.commit()
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prospecto {id_prospecto} no encontrado.",
        )

    return ExtenderTrialOut(
        id_prospecto=row[0],
        nombre=row[1],
        fecha_anterior=row[2],
        fecha_nueva=row[3],
        dias_extendidos=int(row[4]),
    )


@router.post(
    "/limpiar-trials-vencidos",
    response_model=LimpiezaTrialsOut,
    summary="Marca como Inadecuado a prospectos con trial vencido (SP)",
)
def ejecutar_limpieza_trials(db: Session = Depends(get_db)) -> LimpiezaTrialsOut:
    """
    El SP recorre la tabla buscando trials vencidos cuyo prospecto no
    es Convertido ni Inadecuado y los marca. El trigger BEFORE UPDATE
    fuerza puntuacion = 0 automáticamente y el de auditoría deja
    bitácora de cada cambio.
    """
    try:
        cursor = db.connection().connection.cursor()
        cursor.callproc("sp_marcar_trials_vencidos")
        row = cursor.fetchone()
        cursor.close()
        db.commit()
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))

    if row is None:
        return LimpiezaTrialsOut(prospectos_marcados=0, fecha_proceso=row)

    return LimpiezaTrialsOut(
        prospectos_marcados=int(row[0]),
        fecha_proceso=row[1],
    )


# =====================================================================
#  FUNCIONES UDF
# =====================================================================
@router.get(
    "/funciones/nivel-interes",
    response_model=NivelInteresOut,
    summary="Etiqueta cualitativa del scoring (SELECT fn_nivel_interes)",
)
def fn_nivel_interes_endpoint(
    puntuacion: int = Query(..., ge=0),
    db: Session = Depends(get_db),
) -> NivelInteresOut:
    """
    Llama a la UDF `fn_nivel_interes(puntuacion)` para devolver
    'Alto', 'Medio' o 'Bajo'. Sustituye la lógica duplicada que vivía
    en JavaScript.
    """
    nivel = db.scalar(
        text("SELECT fn_nivel_interes(:p)").bindparams(p=puntuacion)
    )
    return NivelInteresOut(puntuacion=puntuacion, nivel_interes=nivel)


@router.get(
    "/funciones/dias-restantes/{id_prospecto}",
    response_model=DiasRestantesTrialOut,
    summary="Días restantes del trial del prospecto (SELECT fn_dias_restantes_trial)",
)
def fn_dias_restantes_endpoint(
    id_prospecto: int, db: Session = Depends(get_db)
) -> DiasRestantesTrialOut:
    """Llama a la UDF y devuelve también `fecha_fin_prueba` por comodidad."""
    dias = db.scalar(
        text("SELECT fn_dias_restantes_trial(:p)").bindparams(p=id_prospecto)
    )
    fecha = db.scalar(
        text(
            "SELECT fecha_fin_prueba FROM PROSPECTO WHERE id_prospecto = :p"
        ).bindparams(p=id_prospecto)
    )
    return DiasRestantesTrialOut(
        id_prospecto=id_prospecto,
        dias_restantes=dias,
        fecha_fin_prueba=fecha,
    )


@router.get(
    "/funciones/lifetime-value/{id_cliente}",
    response_model=LifetimeValueOut,
    summary="Lifetime value del cliente (SELECT fn_lifetime_value)",
)
def fn_lifetime_value_endpoint(
    id_cliente: int, db: Session = Depends(get_db)
) -> LifetimeValueOut:
    """LTV = SUM(monto) de ventas Pagadas del cliente."""
    total = db.scalar(
        text("SELECT fn_lifetime_value(:c)").bindparams(c=id_cliente)
    ) or Decimal("0")
    return LifetimeValueOut(
        id_cliente=id_cliente,
        lifetime_value=Decimal(str(total)),
    )


# =====================================================================
#  AUDITORÍA (poblada por trigger — almacenada en REPORTE)
# =====================================================================
@router.get(
    "/auditoria",
    response_model=List[AuditoriaEventoOut],
    summary="Bitácora de cambios de estado del prospecto (poblada por trigger)",
)
def listar_auditoria(
    id_prospecto: int | None = Query(None, description="Filtra por prospecto."),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AuditoriaEventoOut]:
    """
    El trigger `trg_audit_estado_prospecto` inserta una fila en la
    tabla REPORTE por cada cambio de estado de un prospecto, usando
    tipo_reporte='Auditoria Estado Prospecto' y el campo `resultado`
    como JSON. Aquí lo leemos, lo parseamos y, si se pidió, lo
    filtramos por id_prospecto.
    """
    stmt = (
        select(Reporte)
        .where(Reporte.tipo_reporte == AUDIT_TIPO)
        .order_by(Reporte.fecha_generacion.desc())
        .limit(limit if id_prospecto is None else 500)
    )
    rows = list(db.scalars(stmt).all())

    eventos: list[AuditoriaEventoOut] = []
    for r in rows:
        try:
            data = json.loads(r.resultado or "{}")
        except json.JSONDecodeError:
            continue
        if id_prospecto is not None and data.get("id_prospecto") != id_prospecto:
            continue
        eventos.append(
            AuditoriaEventoOut(
                id_reporte=r.id_reporte,
                fecha_evento=r.fecha_generacion,
                id_prospecto=data.get("id_prospecto"),
                estado_anterior=data.get("estado_anterior"),
                estado_nuevo=data.get("estado_nuevo"),
                puntuacion=data.get("puntuacion"),
            )
        )
        if len(eventos) >= limit:
            break
    return eventos