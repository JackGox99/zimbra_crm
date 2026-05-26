"""Router CRUD para CLIENTE."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter()


@router.get("/", response_model=List[ClienteOut], summary="Listar clientes")
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Cliente]:
    stmt = select(Cliente).order_by(Cliente.id_cliente).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_cliente}",
    response_model=ClienteOut,
    summary="Obtener cliente por id",
)
def obtener_cliente(id_cliente: int, db: Session = Depends(get_db)) -> Cliente:
    obj = db.get(Cliente, id_cliente)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return obj


@router.post(
    "/",
    response_model=ClienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente",
)
def crear_cliente(
    payload: ClienteCreate, db: Session = Depends(get_db)
) -> Cliente:
    obj = Cliente(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo crear el cliente: correo duplicado, prospecto "
                f"ya convertido o FK inválida. Detalle: {e.orig}"
            ),
        )
    db.refresh(obj)
    return obj


@router.put(
    "/{id_cliente}",
    response_model=ClienteOut,
    summary="Actualizar cliente",
)
def actualizar_cliente(
    id_cliente: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
) -> Cliente:
    obj = db.get(Cliente, id_cliente)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
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
    "/{id_cliente}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar cliente",
)
def eliminar_cliente(id_cliente: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Cliente, id_cliente)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el cliente tiene ventas asociadas.",
        )
