"""
Router CRUD para PLANTILLA_COMUNICACION y COMUNICACION_ENVIADA.

Se exponen DOS APIRouter en este archivo:
  * `router_plantillas`  → /api/plantillas/...
  * `router_envios`      → /api/comunicaciones/...

Tener dos routers separados pero declarados en el mismo módulo refleja
que ambas entidades son aspectos del subsistema de comunicaciones y
permite que Swagger UI los agrupe con tags distintos.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.comunicacion_enviada import ComunicacionEnviada
from app.models.plantilla_comunicacion import PlantillaComunicacion
from app.schemas.comunicacion_enviada import (
    ComunicacionEnviadaCreate,
    ComunicacionEnviadaOut,
    ComunicacionEnviadaUpdate,
    EstadoEnvio,
)
from app.schemas.plantilla_comunicacion import (
    PlantillaComunicacionCreate,
    PlantillaComunicacionOut,
    PlantillaComunicacionUpdate,
)

# =====================================================================
#  PLANTILLAS DE COMUNICACIÓN
# =====================================================================
router_plantillas = APIRouter()


@router_plantillas.get(
    "/",
    response_model=List[PlantillaComunicacionOut],
    summary="Listar plantillas",
)
def listar_plantillas(
    activa: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[PlantillaComunicacion]:
    stmt = select(PlantillaComunicacion).order_by(PlantillaComunicacion.id_plantilla)
    if activa is not None:
        stmt = stmt.where(PlantillaComunicacion.activa == activa)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router_plantillas.get(
    "/{id_plantilla}",
    response_model=PlantillaComunicacionOut,
    summary="Obtener plantilla por id",
)
def obtener_plantilla(
    id_plantilla: int, db: Session = Depends(get_db)
) -> PlantillaComunicacion:
    obj = db.get(PlantillaComunicacion, id_plantilla)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return obj


@router_plantillas.post(
    "/",
    response_model=PlantillaComunicacionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear plantilla",
)
def crear_plantilla(
    payload: PlantillaComunicacionCreate, db: Session = Depends(get_db)
) -> PlantillaComunicacion:
    obj = PlantillaComunicacion(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router_plantillas.put(
    "/{id_plantilla}",
    response_model=PlantillaComunicacionOut,
    summary="Actualizar plantilla",
)
def actualizar_plantilla(
    id_plantilla: int,
    payload: PlantillaComunicacionUpdate,
    db: Session = Depends(get_db),
) -> PlantillaComunicacion:
    obj = db.get(PlantillaComunicacion, id_plantilla)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router_plantillas.delete(
    "/{id_plantilla}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar plantilla",
)
def eliminar_plantilla(
    id_plantilla: int, db: Session = Depends(get_db)
) -> None:
    obj = db.get(PlantillaComunicacion, id_plantilla)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: la plantilla tiene envíos asociados.",
        )


# =====================================================================
#  COMUNICACIONES ENVIADAS
# =====================================================================
router_envios = APIRouter()


@router_envios.get(
    "/",
    response_model=List[ComunicacionEnviadaOut],
    summary="Listar comunicaciones enviadas",
)
def listar_envios(
    estado: EstadoEnvio | None = Query(None),
    id_prospecto: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ComunicacionEnviada]:
    stmt = select(ComunicacionEnviada).order_by(
        ComunicacionEnviada.fecha_envio.desc()
    )
    if estado is not None:
        stmt = stmt.where(ComunicacionEnviada.estado_envio == estado)
    if id_prospecto is not None:
        stmt = stmt.where(ComunicacionEnviada.id_prospecto == id_prospecto)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router_envios.get(
    "/{id_comunicacion}",
    response_model=ComunicacionEnviadaOut,
    summary="Obtener envío por id",
)
def obtener_envio(
    id_comunicacion: int, db: Session = Depends(get_db)
) -> ComunicacionEnviada:
    obj = db.get(ComunicacionEnviada, id_comunicacion)
    if not obj:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return obj


@router_envios.post(
    "/",
    response_model=ComunicacionEnviadaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar envío de comunicación",
)
def crear_envio(
    payload: ComunicacionEnviadaCreate, db: Session = Depends(get_db)
) -> ComunicacionEnviada:
    obj = ComunicacionEnviada(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router_envios.put(
    "/{id_comunicacion}",
    response_model=ComunicacionEnviadaOut,
    summary="Actualizar envío",
)
def actualizar_envio(
    id_comunicacion: int,
    payload: ComunicacionEnviadaUpdate,
    db: Session = Depends(get_db),
) -> ComunicacionEnviada:
    obj = db.get(ComunicacionEnviada, id_comunicacion)
    if not obj:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(obj)
    return obj


@router_envios.delete(
    "/{id_comunicacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar envío",
)
def eliminar_envio(
    id_comunicacion: int, db: Session = Depends(get_db)
) -> None:
    obj = db.get(ComunicacionEnviada, id_comunicacion)
    if not obj:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    db.delete(obj)
    db.commit()
