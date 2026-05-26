"""
Router CRUD para INTERACCION_MARKETING.

El endpoint transaccional `POST /registrar` (inserta + actualiza
puntuación del prospecto + promueve a Calificado, todo en una
transacción ACID) se monta en el paso siguiente, sobre el servicio
`app.services.scoring_service`.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaccion_marketing import InteraccionMarketing
from app.schemas.interaccion_marketing import (
    InteraccionMarketingCreate,
    InteraccionMarketingOut,
    InteraccionMarketingUpdate,
    RegistrarInteraccionOut,
)
from app.services.scoring_service import (
    registrar_interaccion as svc_registrar_interaccion,
)

router = APIRouter()


# =====================================================================
#  ENDPOINT TRANSACCIONAL — registrar interacción + recalcular scoring
# =====================================================================
@router.post(
    "/registrar",
    response_model=RegistrarInteraccionOut,
    summary="Registrar interacción y recalcular scoring (transacción ACID)",
)
def registrar_interaccion_endpoint(
    payload: InteraccionMarketingCreate, db: Session = Depends(get_db)
) -> RegistrarInteraccionOut:
    """
    Flujo dentro de UNA transacción:
      1. INSERT en INTERACCION_MARKETING.
      2. UPDATE puntuacion del prospecto (+ peso_scoring).
      3. Si la nueva puntuación cruza el umbral (15) y el estado es
         promovible, UPDATE estado a 'Calificado'.
    """
    try:
        interaccion, nueva_puntuacion, promovido = svc_registrar_interaccion(
            db,
            accion=payload.accion,
            peso_scoring=payload.peso_scoring,
            id_prospecto=payload.id_prospecto,
            id_campana=payload.id_campana,
            fecha_interaccion=payload.fecha_interaccion,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    mensaje = (
        f"Interacción registrada. Puntuación actualizada a {nueva_puntuacion}."
    )
    if promovido:
        mensaje += " El prospecto fue promovido a 'Calificado'."
    return RegistrarInteraccionOut(
        interaccion=InteraccionMarketingOut.model_validate(interaccion),
        puntuacion_actualizada=nueva_puntuacion,
        prospecto_calificado_ahora=promovido,
        mensaje=mensaje,
    )


@router.get(
    "/",
    response_model=List[InteraccionMarketingOut],
    summary="Listar interacciones",
)
def listar_interacciones(
    id_prospecto: int | None = Query(None, description="Filtra por prospecto."),
    id_campana: int | None = Query(None, description="Filtra por campaña."),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[InteraccionMarketing]:
    stmt = select(InteraccionMarketing).order_by(
        InteraccionMarketing.fecha_interaccion.desc()
    )
    if id_prospecto is not None:
        stmt = stmt.where(InteraccionMarketing.id_prospecto == id_prospecto)
    if id_campana is not None:
        stmt = stmt.where(InteraccionMarketing.id_campana == id_campana)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_interaccion}",
    response_model=InteraccionMarketingOut,
    summary="Obtener interacción por id",
)
def obtener_interaccion(
    id_interaccion: int, db: Session = Depends(get_db)
) -> InteraccionMarketing:
    obj = db.get(InteraccionMarketing, id_interaccion)
    if not obj:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return obj


@router.post(
    "/",
    response_model=InteraccionMarketingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear interacción (sin recalcular scoring)",
)
def crear_interaccion(
    payload: InteraccionMarketingCreate, db: Session = Depends(get_db)
) -> InteraccionMarketing:
    """
    Insertar manualmente una interacción **sin** actualizar el scoring.

    Para el flujo transaccional que también actualiza la puntuación del
    prospecto y lo promueve a 'Calificado' si pasa el umbral, ver el
    endpoint `POST /api/interacciones/registrar` (paso 7).
    """
    obj = InteraccionMarketing(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"FK inválida o restricción violada: {e.orig}",
        )
    db.refresh(obj)
    return obj


@router.put(
    "/{id_interaccion}",
    response_model=InteraccionMarketingOut,
    summary="Actualizar interacción",
)
def actualizar_interaccion(
    id_interaccion: int,
    payload: InteraccionMarketingUpdate,
    db: Session = Depends(get_db),
) -> InteraccionMarketing:
    obj = db.get(InteraccionMarketing, id_interaccion)
    if not obj:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
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
    "/{id_interaccion}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar interacción",
)
def eliminar_interaccion(
    id_interaccion: int, db: Session = Depends(get_db)
) -> None:
    obj = db.get(InteraccionMarketing, id_interaccion)
    if not obj:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    db.delete(obj)
    db.commit()
