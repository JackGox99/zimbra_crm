"""
Router CRUD para PROSPECTO.

Incluye el endpoint consultivo `GET /pruebas-por-vencer` que cubre el
requerimiento RF-008 (monitoreo del periodo de prueba de 60 días).

Los endpoints transaccionales `POST /{id}/marcar-inadecuado` y
`POST /interacciones/registrar` se delegan a los servicios y se
montan en el paso siguiente (`scoring_service.py` y la lógica que vive
en `routers/interacciones.py`).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prospecto import Prospecto
from app.schemas.prospecto import (
    EstadoProspecto,
    ProspectoCreate,
    ProspectoOut,
    ProspectoUpdate,
)
from app.services.scoring_service import (
    marcar_inadecuado as svc_marcar_inadecuado,
)

router = APIRouter()


# =====================================================================
#  ENDPOINT TRANSACCIONAL — marcar prospecto como Inadecuado
# =====================================================================
@router.post(
    "/{id_prospecto}/marcar-inadecuado",
    response_model=ProspectoOut,
    summary="Marcar prospecto como 'Inadecuado' (transacción ACID)",
)
def marcar_inadecuado_endpoint(
    id_prospecto: int, db: Session = Depends(get_db)
) -> Prospecto:
    """
    En una sola transacción atómica:
      1. UPDATE estado a 'Inadecuado'.
      2. UPDATE puntuacion = 0.

    Si la operación falla a mitad de camino, ningún cambio queda
    persistido.
    """
    try:
        return svc_marcar_inadecuado(db, id_prospecto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# IMPORTANTE: este endpoint debe declararse ANTES que `/{id_prospecto}`
# porque ambos comparten el prefijo. FastAPI resuelve rutas en orden de
# declaración, así que si /{id_prospecto} viniera primero, capturaría
# "pruebas-por-vencer" como un id inválido.
@router.get(
    "/pruebas-por-vencer",
    response_model=List[ProspectoOut],
    summary="Prospectos cuyo periodo de prueba termina en N días",
)
def prospectos_prueba_por_vencer(
    dias: int = Query(7, ge=1, le=60, description="Ventana hacia el futuro."),
    db: Session = Depends(get_db),
) -> list[Prospecto]:
    """
    Devuelve prospectos con `fecha_fin_prueba` entre hoy y hoy+N días.
    Cubre el requerimiento funcional RF-008.
    """
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    stmt = (
        select(Prospecto)
        .where(Prospecto.fecha_fin_prueba.is_not(None))
        .where(Prospecto.fecha_fin_prueba >= hoy)
        .where(Prospecto.fecha_fin_prueba <= limite)
        .order_by(Prospecto.fecha_fin_prueba)
    )
    return list(db.scalars(stmt).all())


@router.get(
    "/",
    response_model=List[ProspectoOut],
    summary="Listar prospectos (con filtro opcional por estado)",
)
def listar_prospectos(
    estado: EstadoProspecto | None = Query(
        None, description="Filtra por estado exacto."
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Prospecto]:
    stmt = select(Prospecto).order_by(Prospecto.id_prospecto)
    if estado is not None:
        stmt = stmt.where(Prospecto.estado == estado)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_prospecto}",
    response_model=ProspectoOut,
    summary="Obtener prospecto por id",
)
def obtener_prospecto(
    id_prospecto: int, db: Session = Depends(get_db)
) -> Prospecto:
    prospecto = db.get(Prospecto, id_prospecto)
    if not prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    return prospecto


@router.post(
    "/",
    response_model=ProspectoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear prospecto",
)
def crear_prospecto(
    payload: ProspectoCreate, db: Session = Depends(get_db)
) -> Prospecto:
    prospecto = Prospecto(**payload.model_dump())
    db.add(prospecto)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo crear el prospecto: correo duplicado o "
                f"campaña inexistente. Detalle: {e.orig}"
            ),
        )
    db.refresh(prospecto)
    return prospecto


@router.put(
    "/{id_prospecto}",
    response_model=ProspectoOut,
    summary="Actualizar prospecto",
)
def actualizar_prospecto(
    id_prospecto: int,
    payload: ProspectoUpdate,
    db: Session = Depends(get_db),
) -> Prospecto:
    prospecto = db.get(Prospecto, id_prospecto)
    if not prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(prospecto, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integridad: {e.orig}")
    db.refresh(prospecto)
    return prospecto


@router.delete(
    "/{id_prospecto}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar prospecto",
)
def eliminar_prospecto(
    id_prospecto: int, db: Session = Depends(get_db)
) -> None:
    prospecto = db.get(Prospecto, id_prospecto)
    if not prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    db.delete(prospecto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar: el prospecto tiene interacciones, "
                "comunicaciones, propuestas o un cliente asociado."
            ),
        )
