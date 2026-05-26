"""
Router CRUD para CAMPANA.

Endpoints estándar de creación / lectura / actualización / borrado de
campañas de marketing. No incluye lógica transaccional compleja: cada
operación es una transacción corta confirmada con `db.commit()` o
revertida con `db.rollback()` si MySQL rechaza la operación
(violación de CHECK o de integridad referencial).
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campana import Campana
from app.schemas.campana import CampanaCreate, CampanaOut, CampanaUpdate

router = APIRouter()


@router.get("/", response_model=List[CampanaOut], summary="Listar campañas")
def listar_campanas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Campana]:
    """Lista paginada de campañas (orden por id ascendente)."""
    stmt = select(Campana).order_by(Campana.id_campana).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_campana}",
    response_model=CampanaOut,
    summary="Obtener campaña por id",
)
def obtener_campana(id_campana: int, db: Session = Depends(get_db)) -> Campana:
    campana = db.get(Campana, id_campana)
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    return campana


@router.post(
    "/",
    response_model=CampanaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear campaña",
)
def crear_campana(
    payload: CampanaCreate, db: Session = Depends(get_db)
) -> Campana:
    campana = Campana(**payload.model_dump())
    db.add(campana)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(campana)
    return campana


@router.put(
    "/{id_campana}",
    response_model=CampanaOut,
    summary="Actualizar campaña",
)
def actualizar_campana(
    id_campana: int,
    payload: CampanaUpdate,
    db: Session = Depends(get_db),
) -> Campana:
    campana = db.get(Campana, id_campana)
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(campana, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(campana)
    return campana


@router.delete(
    "/{id_campana}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar campaña",
)
def eliminar_campana(id_campana: int, db: Session = Depends(get_db)) -> None:
    campana = db.get(Campana, id_campana)
    if not campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    db.delete(campana)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar la campaña: tiene prospectos, "
                "interacciones, comunicaciones o reportes asociados."
            ),
        )
