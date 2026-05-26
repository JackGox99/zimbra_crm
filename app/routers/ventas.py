"""
Router CRUD para VENTA.

El endpoint transaccional estrella `POST /cerrar-venta` (con SAVEPOINTs
para creación de cliente y promoción del prospecto) se monta en el paso
siguiente sobre el servicio `app.services.venta_service`.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venta import Venta
from app.schemas.venta import (
    CerrarVentaIn,
    CerrarVentaOut,
    EstadoVenta,
    VentaCreate,
    VentaOut,
    VentaUpdate,
)
from app.services.venta_service import (
    anular_venta as svc_anular_venta,
    cerrar_venta as svc_cerrar_venta,
)

router = APIRouter()


# =====================================================================
#  ENDPOINT TRANSACCIONAL ESTRELLA — cierre de venta con SAVEPOINTs
# =====================================================================
@router.post(
    "/cerrar-venta",
    response_model=CerrarVentaOut,
    summary="Cerrar una venta a partir de una propuesta (transacción ACID)",
)
def cerrar_venta_endpoint(
    payload: CerrarVentaIn, db: Session = Depends(get_db)
) -> CerrarVentaOut:
    """
    Ejecuta el flujo transaccional completo:

      1. SP1 — actualiza estado de la propuesta a 'Aceptada'.
      2. SP2 — crea el cliente desde el prospecto. Si ya existe
               (recompra), hace ROLLBACK TO sp2 y reutiliza el cliente
               preexistente.
      3. SP3 — promueve el prospecto a 'Convertido' y registra la venta
               con monto = valor_estimado de la propuesta.
      COMMIT — confirma todo al final.

    Si CUALQUIER paso falla irrecuperablemente, la transacción completa
    se revierte y nada queda persistido.
    """
    try:
        venta, cliente_creado = svc_cerrar_venta(
            db,
            id_propuesta=payload.id_propuesta,
            metodo_pago=payload.metodo_pago or "Transferencia",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Integridad: {e.orig}")

    mensaje = (
        "Venta cerrada exitosamente. "
        + (
            "Cliente nuevo creado."
            if cliente_creado
            else "Cliente preexistente reutilizado (caso recompra)."
        )
    )
    return CerrarVentaOut(
        venta=VentaOut.model_validate(venta),
        cliente_creado=cliente_creado,
        mensaje=mensaje,
    )


# =====================================================================
#  Anular venta — transacción que naturalmente puede hacer ROLLBACK
# =====================================================================
@router.post(
    "/{id_venta}/anular",
    response_model=VentaOut,
    summary="Anular una venta (transacción con posible ROLLBACK)",
)
def anular_venta_endpoint(
    id_venta: int, db: Session = Depends(get_db)
) -> Venta:
    """
    Anula una venta dentro de una transacción atómica.

    * Si todo es válido → UPDATE → COMMIT.
    * Si la venta ya estaba anulada (regla de negocio) → ROLLBACK.
    """
    try:
        return svc_anular_venta(db, id_venta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[VentaOut], summary="Listar ventas")
def listar_ventas(
    estado: EstadoVenta | None = Query(None),
    id_cliente: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Venta]:
    stmt = select(Venta).order_by(Venta.fecha_venta.desc())
    if estado is not None:
        stmt = stmt.where(Venta.estado == estado)
    if id_cliente is not None:
        stmt = stmt.where(Venta.id_cliente == id_cliente)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get(
    "/{id_venta}",
    response_model=VentaOut,
    summary="Obtener venta por id",
)
def obtener_venta(id_venta: int, db: Session = Depends(get_db)) -> Venta:
    obj = db.get(Venta, id_venta)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return obj


@router.post(
    "/",
    response_model=VentaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear venta directa (sin SAVEPOINTs)",
)
def crear_venta(payload: VentaCreate, db: Session = Depends(get_db)) -> Venta:
    """
    Creación directa de una venta. Para el flujo completo de cierre
    transaccional con SAVEPOINTs (que crea el cliente y promueve al
    prospecto a 'Convertido') ver `POST /api/ventas/cerrar-venta`.
    """
    obj = Venta(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo crear la venta: propuesta ya vendida, "
                f"cliente inexistente o monto inválido. Detalle: {e.orig}"
            ),
        )
    db.refresh(obj)
    return obj


@router.put(
    "/{id_venta}",
    response_model=VentaOut,
    summary="Actualizar venta",
)
def actualizar_venta(
    id_venta: int,
    payload: VentaUpdate,
    db: Session = Depends(get_db),
) -> Venta:
    obj = db.get(Venta, id_venta)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
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
    "/{id_venta}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar venta",
)
def eliminar_venta(id_venta: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Venta, id_venta)
    if not obj:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(obj)
    db.commit()
