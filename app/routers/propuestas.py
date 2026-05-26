"""Router CRUD para PROPUESTA."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.propuesta import Propuesta
from app.schemas.propuesta import (
    EstadoPropuesta,
    PropuestaCreate,
    PropuestaOut,
    PropuestaUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[PropuestaOut],
    summary="Listar propuestas (con filtro opcional por estado)",
)
def listar_propuestas(
    estado: EstadoPropuesta | None = Query(None),
    id_prospecto: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Propuesta]:
    stmt = select(Propuesta).order_by(Propuesta.id_propuesta.desc())
    if estado is not None:
        stmt = stmt.where(Propuesta.estado == estado)
    if id_prospecto is not None:
        stmt = stmt.where(Propuesta.id_prospecto == id_prospecto)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_propuesta}",
    response_model=PropuestaOut,
    summary="Obtener propuesta por id",
)
def obtener_propuesta(
    id_propuesta: int, db: Session = Depends(get_db)
) -> Propuesta:
    obj = db.get(Propuesta, id_propuesta)
    if not obj:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return obj


@router.post(
    "/",
    response_model=PropuestaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear propuesta",
)
def crear_propuesta(
    payload: PropuestaCreate, db: Session = Depends(get_db)
) -> Propuesta:
    obj = Propuesta(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router.put(
    "/{id_propuesta}",
    response_model=PropuestaOut,
    summary="Actualizar propuesta",
)
def actualizar_propuesta(
    id_propuesta: int,
    payload: PropuestaUpdate,
    db: Session = Depends(get_db),
) -> Propuesta:
    obj = db.get(Propuesta, id_propuesta)
    if not obj:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
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
    "/{id_propuesta}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar propuesta",
)
def eliminar_propuesta(
    id_propuesta: int, db: Session = Depends(get_db)
) -> None:
    obj = db.get(Propuesta, id_propuesta)
    if not obj:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: la propuesta tiene una venta asociada.",
        )
