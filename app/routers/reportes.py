"""
Router para REPORTE.

Incluye:
  * CRUD básico sobre la tabla REPORTE (guardado de reportes generados).
  * Endpoints consultivos parametrizados que computan al vuelo:
      - `GET /conversion`               → embudo total.
      - `GET /campanas/{id}/rendimiento` → ROI de una campaña concreta.

Las consultas usan agregaciones SQL en lugar de cargar registros uno a
uno, lo cual mantiene la operación dentro de una sola transacción
implícita corta (consistencia de lectura por la sesión).
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campana import Campana
from app.models.cliente import Cliente
from app.models.propuesta import Propuesta
from app.models.prospecto import Prospecto
from app.models.reporte import Reporte
from app.models.venta import Venta
from app.schemas.reporte import (
    EmbudoConversionOut,
    RendimientoCampanaOut,
    ReporteCreate,
    ReporteOut,
    ReporteUpdate,
)

router = APIRouter()


# =====================================================================
#  Endpoints consultivos — se declaran ANTES de los CRUD para que rutas
#  como "/conversion" no sean capturadas como id_reporte.
# =====================================================================
@router.get(
    "/conversion",
    response_model=EmbudoConversionOut,
    summary="Embudo de conversión de marketing → ventas",
)
def reporte_conversion(db: Session = Depends(get_db)) -> EmbudoConversionOut:
    """
    Calcula el embudo de conversión usando consultas agregadas (`COUNT`,
    `SUM`) sobre las tablas PROSPECTO, CLIENTE y VENTA.
    """
    total_prospectos = db.scalar(select(func.count(Prospecto.id_prospecto))) or 0
    total_activos = (
        db.scalar(
            select(func.count(Prospecto.id_prospecto)).where(
                Prospecto.estado != "Inadecuado"
            )
        )
        or 0
    )
    total_calificados = (
        db.scalar(
            select(func.count(Prospecto.id_prospecto)).where(
                Prospecto.estado.in_(["Calificado", "Convertido"])
            )
        )
        or 0
    )
    total_clientes = db.scalar(select(func.count(Cliente.id_cliente))) or 0
    total_ventas_pagadas = (
        db.scalar(
            select(func.count(Venta.id_venta)).where(Venta.estado == "Pagada")
        )
        or 0
    )
    ingresos_totales: Decimal = db.scalar(
        select(func.coalesce(func.sum(Venta.monto), 0)).where(
            Venta.estado == "Pagada"
        )
    ) or Decimal("0")

    return EmbudoConversionOut(
        total_prospectos=total_prospectos,
        total_prospectos_activos=total_activos,
        total_calificados=total_calificados,
        total_clientes=total_clientes,
        total_ventas_pagadas=total_ventas_pagadas,
        ingresos_totales=ingresos_totales,
    )


@router.get(
    "/campanas/{id_campana}/rendimiento",
    response_model=RendimientoCampanaOut,
    summary="ROI / rendimiento de una campaña",
)
def reporte_rendimiento_campana(
    id_campana: int, db: Session = Depends(get_db)
) -> RendimientoCampanaOut:
    """
    ROI = (ingresos − presupuesto) / presupuesto × 100. Los ingresos
    son ventas pagadas cuyos clientes provienen de prospectos
    capturados por la campaña indicada.
    """
    campana = db.get(Campana, id_campana)
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    prospectos_generados = (
        db.scalar(
            select(func.count(Prospecto.id_prospecto)).where(
                Prospecto.id_campana_origen == id_campana
            )
        )
        or 0
    )
    prospectos_calificados = (
        db.scalar(
            select(func.count(Prospecto.id_prospecto))
            .where(Prospecto.id_campana_origen == id_campana)
            .where(Prospecto.estado.in_(["Calificado", "Convertido"]))
        )
        or 0
    )

    # Clientes que provienen de prospectos de esta campaña.
    stmt_clientes_id = (
        select(Cliente.id_cliente)
        .join(Prospecto, Prospecto.id_prospecto == Cliente.id_prospecto)
        .where(Prospecto.id_campana_origen == id_campana)
    )
    clientes_ids = list(db.scalars(stmt_clientes_id).all())
    clientes_convertidos = len(clientes_ids)

    if clientes_ids:
        ventas_cerradas = (
            db.scalar(
                select(func.count(Venta.id_venta))
                .where(Venta.id_cliente.in_(clientes_ids))
                .where(Venta.estado == "Pagada")
            )
            or 0
        )
        ingresos_generados: Decimal = db.scalar(
            select(func.coalesce(func.sum(Venta.monto), 0))
            .where(Venta.id_cliente.in_(clientes_ids))
            .where(Venta.estado == "Pagada")
        ) or Decimal("0")
    else:
        ventas_cerradas = 0
        ingresos_generados = Decimal("0")

    presupuesto = campana.presupuesto
    if presupuesto and presupuesto > 0:
        roi = float((ingresos_generados - presupuesto) / presupuesto * 100)
    else:
        roi = None

    return RendimientoCampanaOut(
        id_campana=campana.id_campana,
        nombre_campana=campana.nombre,
        tipo=campana.tipo,
        canal=campana.canal,
        presupuesto=presupuesto,
        prospectos_generados=prospectos_generados,
        prospectos_calificados=prospectos_calificados,
        clientes_convertidos=clientes_convertidos,
        ventas_cerradas=ventas_cerradas,
        ingresos_generados=ingresos_generados,
        roi_porcentaje=roi,
    )


# =====================================================================
#  CRUD sobre la tabla REPORTE (guardado de reportes generados).
# =====================================================================
@router.get(
    "/",
    response_model=List[ReporteOut],
    summary="Listar reportes guardados",
)
def listar_reportes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Reporte]:
    stmt = select(Reporte).order_by(Reporte.fecha_generacion.desc())
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_reporte}",
    response_model=ReporteOut,
    summary="Obtener reporte por id",
)
def obtener_reporte(id_reporte: int, db: Session = Depends(get_db)) -> Reporte:
    obj = db.get(Reporte, id_reporte)
    if not obj:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return obj


@router.post(
    "/",
    response_model=ReporteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar un reporte",
)
def crear_reporte(payload: ReporteCreate, db: Session = Depends(get_db)) -> Reporte:
    obj = Reporte(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router.put(
    "/{id_reporte}",
    response_model=ReporteOut,
    summary="Actualizar reporte",
)
def actualizar_reporte(
    id_reporte: int,
    payload: ReporteUpdate,
    db: Session = Depends(get_db),
) -> Reporte:
    obj = db.get(Reporte, id_reporte)
    if not obj:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router.delete(
    "/{id_reporte}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar reporte",
)
def eliminar_reporte(id_reporte: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Reporte, id_reporte)
    if not obj:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    db.delete(obj)
    db.commit()
