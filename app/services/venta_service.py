"""
Servicio transaccional de cierre de ventas.

Demuestra explícitamente las propiedades ACID:

  * Atomicidad   — Todo el flujo (actualización de propuesta, creación
                   del cliente, conversión del prospecto, registro de la
                   venta) ocurre dentro de UNA transacción `with
                   db.begin():`. Si cualquier paso falla, NADA queda
                   persistido en la base de datos.

  * Consistencia — El flujo respeta las restricciones del esquema:
                   los CHECK (monto > 0, valor_estimado >= 0), las
                   claves UNIQUE (correo, id_prospecto, id_propuesta) y
                   las claves foráneas (id_cliente, id_propuesta).

  * Aislamiento  — La transacción se ejecuta bajo el nivel REPEATABLE
                   READ (default de InnoDB), lo cual evita lecturas no
                   repetibles y phantom reads dentro de la propia
                   transacción.

  * Durabilidad  — Tras el COMMIT (cierre del `with db.begin():`), los
                   cambios quedan en el redo log de InnoDB y son
                   recuperables aun si la BD se reinicia inesperadamente
                   (siempre que innodb_flush_log_at_trx_commit=1).

Se usan 3 SAVEPOINTs anidados para ilustrar el patrón didáctico
solicitado en la sustentación:

  * SP1 — actualización de propuesta a 'Aceptada'.
  * SP2 — creación del cliente. Si el cliente ya existe (caso recompra
          o reconversión), se hace ROLLBACK TO SAVEPOINT sp2 y se
          recupera el cliente preexistente para continuar.
  * SP3 — promoción del prospecto a 'Convertido' + creación de la venta.
"""

from __future__ import annotations

from datetime import date
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.propuesta import Propuesta
from app.models.venta import Venta


def cerrar_venta(
    db: Session,
    id_propuesta: int,
    metodo_pago: str = "Transferencia",
) -> Tuple[Venta, bool]:
    """
    Cierra una venta a partir de una propuesta aceptada.

    Parámetros:
        db: Sesión SQLAlchemy con `autocommit=False`.
        id_propuesta: PK de la propuesta a cerrar.
        metodo_pago: 'Tarjeta', 'Transferencia', 'PayPal', etc.

    Retorna:
        Tupla `(venta, cliente_creado)`:
          * venta: la instancia Venta recién persistida.
          * cliente_creado: True si se creó un cliente nuevo; False si
            ya existía y se reutilizó (caso recompra).

    Excepciones:
        ValueError       — propuesta inexistente, ya vendida o en estado
                           no convertible (Rechazada / Vencida).
        IntegrityError   — violación irrecuperable de FK/UNIQUE.
    """
    cliente_creado = True

    with db.begin():
        # ----- Carga y validación inicial --------------------------------
        propuesta = db.get(Propuesta, id_propuesta)
        if propuesta is None:
            raise ValueError(f"Propuesta {id_propuesta} no encontrada.")
        if propuesta.estado in ("Rechazada", "Vencida"):
            raise ValueError(
                f"La propuesta {id_propuesta} está en estado "
                f"'{propuesta.estado}'; no puede convertirse en venta."
            )
        if propuesta.venta is not None:
            raise ValueError(
                f"La propuesta {id_propuesta} ya tiene una venta cerrada."
            )

        prospecto = propuesta.prospecto

        # ----- SP1: actualización de propuesta ---------------------------
        # Cualquier excepción dentro de este `with` haría ROLLBACK TO sp1
        # y propagaría el error → la transacción externa también aborta.
        with db.begin_nested():
            propuesta.estado = "Aceptada"
            db.flush()
        # RELEASE SAVEPOINT sp1

        # ----- SP2: creación del cliente (con posibilidad de recompra) ---
        sp2 = db.begin_nested()
        try:
            cliente = Cliente(
                nombre=prospecto.nombre,
                correo=prospecto.correo,
                empresa=prospecto.empresa,
                telefono=prospecto.telefono,
                fecha_registro=date.today(),
                id_prospecto=prospecto.id_prospecto,
                sync_salesforce=False,
                fecha_ult_sync=None,
            )
            db.add(cliente)
            db.flush()
            sp2.commit()  # RELEASE SAVEPOINT sp2
        except IntegrityError:
            # Caso recompra / reconversión: ya existe un cliente con
            # ese correo o id_prospecto (UNIQUE). Volvemos al estado
            # justo antes de intentar el INSERT y recuperamos el
            # cliente preexistente.
            sp2.rollback()
            cliente_creado = False
            cliente = db.scalar(
                select(Cliente).where(
                    Cliente.id_prospecto == prospecto.id_prospecto
                )
            )
            if cliente is None:
                cliente = db.scalar(
                    select(Cliente).where(Cliente.correo == prospecto.correo)
                )
            if cliente is None:
                # No se pudo recuperar; abortamos toda la transacción.
                raise ValueError(
                    "Conflicto al crear el cliente y no se pudo "
                    "recuperar el existente."
                )

        # ----- SP3: conversión del prospecto + registro de venta ---------
        with db.begin_nested():
            prospecto.estado = "Convertido"
            venta = Venta(
                fecha_venta=date.today(),
                monto=propuesta.valor_estimado,
                estado="Pagada",
                metodo_pago=metodo_pago,
                id_propuesta=propuesta.id_propuesta,
                id_cliente=cliente.id_cliente,
            )
            db.add(venta)
            db.flush()
        # RELEASE SAVEPOINT sp3

    # COMMIT de la transacción externa al salir del `with db.begin():`
    return venta, cliente_creado


def anular_venta(db: Session, id_venta: int) -> Venta:
    """
    Anula una venta dentro de una transacción atómica.

    Reglas de negocio:
      * Si la venta no existe → ValueError → ROLLBACK automático.
      * Si la venta YA está anulada → ValueError → ROLLBACK automático.
      * Caso normal → UPDATE estado='Anulada' → COMMIT.

    Esta función es útil para que el usuario vea en la UI tanto el caso
    feliz (COMMIT) como el caso de error de negocio (ROLLBACK) intentando
    anular dos veces la misma venta.
    """
    with db.begin():
        venta = db.get(Venta, id_venta)
        if venta is None:
            raise ValueError(
                f"La venta {id_venta} no existe. La transacción se revierte."
            )
        if venta.estado == "Anulada":
            raise ValueError(
                f"La venta {id_venta} ya estaba anulada. "
                f"No se puede anular dos veces — la transacción se revierte."
            )
        venta.estado = "Anulada"
        db.flush()
    # COMMIT al salir del with sin excepción
    return venta
