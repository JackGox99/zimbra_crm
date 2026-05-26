"""
Servicio transaccional de scoring de prospectos.

A partir de la Sesión 3, la lógica de actualización de scoring y
promoción a 'Calificado' vive en el trigger
`trg_interaccion_actualiza_scoring` definido al final de
`sql/zimbra_crm.sql`. El servicio en Python solo inserta la
interacción y vuelve a leer al prospecto para devolver al cliente los
valores actualizados por el trigger.

  * Atomicidad: el INSERT y el UPDATE del trigger ocurren en la misma
    transacción. Si el `with db.begin():` aborta, ni la interacción ni
    los cambios del prospecto persisten.

  * Consistencia: la regla de promoción a 'Calificado' siempre se
    cumple, incluso si se inserta una interacción desde fuera del
    backend (Swagger, SQL manual, otra app).

`marcar_inadecuado` además aprovecha el trigger
`trg_prospecto_inadecuado_resetea_score` (BEFORE UPDATE), que fuerza
`puntuacion = 0` cuando el estado pasa a 'Inadecuado'. El servicio
mantiene el `puntuacion = 0` explícito como red de seguridad y para
que el comportamiento sea idéntico aunque el trigger no exista.
"""

from __future__ import annotations

from datetime import datetime
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.campana import Campana
from app.models.interaccion_marketing import InteraccionMarketing
from app.models.prospecto import Prospecto

# Mismo umbral que usa el trigger en MySQL (debe mantenerse sincronizado).
UMBRAL_CALIFICACION: int = 15


def registrar_interaccion(
    db: Session,
    *,
    accion: str,
    peso_scoring: int,
    id_prospecto: int,
    id_campana: int,
    fecha_interaccion: datetime | None = None,
    umbral: int = UMBRAL_CALIFICACION,
) -> Tuple[InteraccionMarketing, int, bool]:
    """
    Registra una interacción y deja que el trigger de la BD actualice
    el scoring y el estado del prospecto.

    Flujo dentro de UNA transacción ACID:
      1. Carga prospecto y campaña (validaciones).
      2. INSERT en INTERACCION_MARKETING.
      3. db.flush() — dispara el trigger trg_interaccion_actualiza_scoring
         que hace UPDATE PROSPECTO SET puntuacion += peso y promueve a
         'Calificado' si supera el umbral.
      4. db.refresh(prospecto) — relee los valores actualizados.

    Retorna:
        (interaccion, puntuacion_final, promovido_a_calificado)
    """
    promovido = False

    with db.begin():
        prospecto = db.get(Prospecto, id_prospecto)
        if prospecto is None:
            raise ValueError(f"Prospecto {id_prospecto} no encontrado.")
        campana = db.get(Campana, id_campana)
        if campana is None:
            raise ValueError(f"Campaña {id_campana} no encontrada.")

        estado_antes = prospecto.estado

        interaccion = InteraccionMarketing(
            accion=accion,
            fecha_interaccion=fecha_interaccion or datetime.now(),
            peso_scoring=peso_scoring,
            id_prospecto=id_prospecto,
            id_campana=id_campana,
        )
        db.add(interaccion)
        db.flush()  # ← Aquí el trigger MySQL actualiza PROSPECTO.

        db.refresh(prospecto)

        promovido = (
            estado_antes in ("Pendiente", "Contactado")
            and prospecto.estado == "Calificado"
        )

    # COMMIT al salir del `with db.begin()`.
    return interaccion, prospecto.puntuacion, promovido


def marcar_inadecuado(db: Session, id_prospecto: int) -> Prospecto:
    """
    Marca un prospecto como 'Inadecuado' y resetea su puntuación a 0.

    El trigger `trg_prospecto_inadecuado_resetea_score` (BEFORE UPDATE)
    también fuerza `puntuacion = 0`; el servicio lo deja explícito como
    intención clara y para que la lógica funcione aunque el trigger no
    esté cargado.
    """
    with db.begin():
        prospecto = db.get(Prospecto, id_prospecto)
        if prospecto is None:
            raise ValueError(f"Prospecto {id_prospecto} no encontrado.")
        prospecto.estado = "Inadecuado"
        prospecto.puntuacion = 0
        db.flush()
    # COMMIT
    return prospecto