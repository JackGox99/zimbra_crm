"""
Script de carga inicial de datos (seed) para Zimbra CRM.

Genera datos realistas usando Faker (locale 'es_CO') manteniendo
integridad referencial entre las 9 tablas:

  * 30 CAMPAÑAS de marketing (variados tipos y canales).
  * 30 PLANTILLAS de comunicación.
  * 60 PROSPECTOS con correos únicos.
  * ~250 INTERACCIONES de marketing (2-7 por prospecto, pesos canónicos).
  * 80 COMUNICACIONES enviadas.
  * 45 PROPUESTAS (la mayoría 'Aceptada' para generar ~30 ventas).
  * 30+ CLIENTES (uno por cada prospecto con propuesta aceptada).
  * 30+ VENTAS (una por cada propuesta aceptada, con su cliente).
  * 30 REPORTES.

Uso:
    python scripts/seed_database.py            # falla si ya hay datos
    python scripts/seed_database.py --reset    # borra y reinserta
    python scripts/seed_database.py --force    # añade aún con datos

Importante:
  * Las interacciones determinan la puntuación final del prospecto.
    Los que superan 15 puntos quedan en estado 'Calificado'.
  * Algunos prospectos (~10%) tienen `fecha_fin_prueba` en los próximos
    7 días, para que el endpoint RF-008 devuelva resultados visibles.
  * Los pesos de scoring siguen lo especificado en la sustentación:
      Apertura=2, Click=3, Visita Precios=5, Descarga Trial=10.
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Hace importable el paquete `app` cuando se ejecuta como script.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from faker import Faker  # noqa: E402
from sqlalchemy import func, select, text  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Campana,
    Cliente,
    ComunicacionEnviada,
    InteraccionMarketing,
    PlantillaComunicacion,
    Propuesta,
    Prospecto,
    Reporte,
    Venta,
)

# Semilla fija para reproducibilidad entre corridas.
fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)


# =====================================================================
#  Catálogos de valores realistas
# =====================================================================
ACCIONES_MARKETING: list[tuple[str, int]] = [
    ("Apertura Correo", 2),
    ("Click Enlace", 3),
    ("Visita Pagina Precios", 5),
    ("Descarga Prueba", 10),
    ("Registro Formulario", 4),
    ("Asistencia Webinar", 6),
    ("Solicitud Demo", 8),
    ("Lectura Documentacion", 1),
]

TIPOS_CAMPANA = [
    "Email", "Webinar", "Banner Web", "Descarga Trial",
    "Eventos", "Redes Sociales", "Google Ads",
]
CANALES_CAMPANA = [
    "Web", "Email", "Redes Sociales", "Eventos Presenciales",
    "Publicidad Digital", "Partners",
]
ESTADOS_CAMPANA = ["Planeada", "Activa", "Finalizada", "Cancelada"]

TIPOS_PLANTILLA = ["Email", "SMS", "Notificacion"]
ASUNTOS_PLANTILLA = [
    "Bienvenido a Zimbra Collaboration Suite",
    "Tu prueba de Zimbra está por terminar",
    "¿Te ayudamos con la migración?",
    "Oferta exclusiva: 20% en planes anuales",
    "Tutorial: configura tu primer dominio",
    "Cliente caso de éxito: empresa multinacional",
    "Recordatorio: webinar técnico esta semana",
    "Comparativa Zimbra vs. competencia",
]

ESTADOS_ENVIO = ["Enviado", "Fallido", "Rebotado", "Abierto"]
ESTADOS_PROPUESTA = ["Pendiente", "Aceptada", "Rechazada", "Vencida"]
ESTADOS_VENTA = ["Pagada", "Pendiente", "Anulada"]
METODOS_PAGO = ["Tarjeta", "Transferencia", "PayPal", "Efectivo"]
TIPOS_REPORTE = [
    "Rendimiento Campana", "Prospectos Calificados",
    "Ventas Periodo", "Conversion Embudo", "ROI Anual",
]


# =====================================================================
#  Helpers
# =====================================================================
def random_date_between(start: date, end: date) -> date:
    """Devuelve una fecha aleatoria entre start y end (inclusive)."""
    if end < start:
        return start
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def ya_esta_seeded(db) -> bool:
    """True si ya hay más prospectos de los que trae el script SQL inicial."""
    count = db.scalar(select(func.count(Prospecto.id_prospecto))) or 0
    return count > 10


def resetear_bd(db) -> None:
    """Borra todas las filas y reinicia los AUTO_INCREMENT."""
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    tablas = [
        "REPORTE", "VENTA", "CLIENTE", "PROPUESTA",
        "COMUNICACION_ENVIADA", "INTERACCION_MARKETING",
        "PROSPECTO", "PLANTILLA_COMUNICACION", "CAMPANA",
    ]
    for tabla in tablas:
        db.execute(text(f"DELETE FROM {tabla}"))
        db.execute(text(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.commit()


# =====================================================================
#  Funciones de inserción por entidad
# =====================================================================
def seed_campanas(db, n: int = 30) -> list[Campana]:
    campanas: list[Campana] = []
    for i in range(n):
        fecha_inicio = random_date_between(date(2024, 6, 1), date(2026, 5, 1))
        fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 180))

        # Estado coherente con las fechas.
        hoy = date.today()
        if fecha_inicio > hoy:
            estado = "Planeada"
        elif fecha_fin < hoy:
            estado = random.choice(["Finalizada", "Cancelada"])
        else:
            estado = "Activa"

        c = Campana(
            nombre=f"{random.choice(TIPOS_CAMPANA)} {fake.bs().capitalize()} {i + 1}",
            tipo=random.choice(TIPOS_CAMPANA),
            canal=random.choice(CANALES_CAMPANA),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            presupuesto=Decimal(str(random.randint(1_000_000, 50_000_000))),
            estado=estado,
        )
        campanas.append(c)
    db.add_all(campanas)
    db.flush()
    return campanas


def seed_plantillas(db, n: int = 30) -> list[PlantillaComunicacion]:
    plantillas: list[PlantillaComunicacion] = []
    for i in range(n):
        tipo = random.choice(TIPOS_PLANTILLA)
        p = PlantillaComunicacion(
            nombre=f"Plantilla {tipo} #{i + 1}",
            asunto=random.choice(ASUNTOS_PLANTILLA),
            cuerpo=fake.paragraph(nb_sentences=5),
            tipo=tipo,
            fecha_creacion=random_date_between(date(2024, 1, 1), date.today()),
            activa=random.random() < 0.85,
        )
        plantillas.append(p)
    db.add_all(plantillas)
    db.flush()
    return plantillas


def seed_prospectos(
    db, campanas: list[Campana], n: int = 60
) -> list[Prospecto]:
    prospectos: list[Prospecto] = []
    correos_usados: set[str] = set()

    for i in range(n):
        # Garantiza correo único.
        for _ in range(20):
            correo = fake.unique.email()
            if correo not in correos_usados:
                correos_usados.add(correo)
                break

        fecha_registro = random_date_between(date(2024, 6, 1), date.today())
        fecha_inicio_prueba: date | None = None
        fecha_fin_prueba: date | None = None

        # 70% tiene periodo de prueba; ~10% lo tiene venciendo pronto
        # (para que el endpoint RF-008 devuelva resultados durante la demo).
        if random.random() < 0.7:
            if i % 10 == 0:
                fecha_fin_prueba = date.today() + timedelta(
                    days=random.randint(1, 7)
                )
                fecha_inicio_prueba = fecha_fin_prueba - timedelta(days=60)
                fecha_registro = fecha_inicio_prueba
            else:
                fecha_inicio_prueba = fecha_registro
                fecha_fin_prueba = fecha_inicio_prueba + timedelta(days=60)

        p = Prospecto(
            nombre=fake.name(),
            correo=correo,
            empresa=fake.company(),
            telefono=fake.phone_number()[:20],
            puntuacion=0,        # se recalcula tras las interacciones
            estado="Pendiente",  # idem
            fecha_registro=fecha_registro,
            fecha_inicio_prueba=fecha_inicio_prueba,
            fecha_fin_prueba=fecha_fin_prueba,
            id_campana_origen=(
                random.choice(campanas).id_campana
                if random.random() < 0.9
                else None
            ),
        )
        prospectos.append(p)
    db.add_all(prospectos)
    db.flush()
    return prospectos


def seed_interacciones(
    db,
    prospectos: list[Prospecto],
    campanas: list[Campana],
) -> list[InteraccionMarketing]:
    """
    Crea 2-7 interacciones por prospecto y recalcula puntuación + estado.

    Los prospectos que superen 15 puntos pasan a 'Calificado'; los que
    superen 5 quedan en 'Contactado'. Un ~8% queda marcado como
    'Inadecuado' aleatoriamente para tener variedad en el dashboard.
    """
    interacciones: list[InteraccionMarketing] = []
    puntuaciones: dict[int, int] = {p.id_prospecto: 0 for p in prospectos}

    for p in prospectos:
        n = random.randint(2, 7)
        for _ in range(n):
            accion, peso = random.choice(ACCIONES_MARKETING)
            fecha = fake.date_time_between(
                start_date=p.fecha_registro, end_date=date.today()
            )
            inter = InteraccionMarketing(
                accion=accion,
                fecha_interaccion=fecha,
                peso_scoring=peso,
                id_prospecto=p.id_prospecto,
                id_campana=random.choice(campanas).id_campana,
            )
            interacciones.append(inter)
            puntuaciones[p.id_prospecto] += peso

    db.add_all(interacciones)

    # Recalcula estado y puntuación basándose en lo acumulado.
    for p in prospectos:
        p.puntuacion = puntuaciones[p.id_prospecto]
        if random.random() < 0.08:
            p.estado = "Inadecuado"
        elif p.puntuacion >= 15:
            p.estado = "Calificado"
        elif p.puntuacion >= 5:
            p.estado = "Contactado"
        else:
            p.estado = "Pendiente"
    db.flush()
    return interacciones


def seed_comunicaciones(
    db,
    plantillas: list[PlantillaComunicacion],
    prospectos: list[Prospecto],
    campanas: list[Campana],
    n: int = 80,
) -> list[ComunicacionEnviada]:
    comunicaciones: list[ComunicacionEnviada] = []
    for _ in range(n):
        p = random.choice(prospectos)
        c = ComunicacionEnviada(
            fecha_envio=fake.date_time_between(
                start_date=p.fecha_registro, end_date=date.today()
            ),
            estado_envio=random.choices(
                ESTADOS_ENVIO, weights=[70, 5, 10, 15]
            )[0],
            id_plantilla=random.choice(plantillas).id_plantilla,
            id_prospecto=p.id_prospecto,
            id_campana=(
                random.choice(campanas).id_campana
                if random.random() < 0.8
                else None
            ),
        )
        comunicaciones.append(c)
    db.add_all(comunicaciones)
    db.flush()
    return comunicaciones


def seed_propuestas(db, prospectos: list[Prospecto], n: int = 45) -> list[Propuesta]:
    """
    Genera propuestas principalmente para prospectos Calificado /
    Contactado, distribuyendo estados con peso fuerte en 'Aceptada'
    para garantizar 30+ ventas posteriormente.
    """
    candidatos = [
        p for p in prospectos if p.estado in ("Calificado", "Contactado")
    ]
    if len(candidatos) < n:
        # Completamos con cualquier prospecto no-Inadecuado.
        extras = [
            p for p in prospectos
            if p.estado != "Inadecuado" and p not in candidatos
        ]
        candidatos.extend(extras)

    random.shuffle(candidatos)
    candidatos = candidatos[:n]

    propuestas: list[Propuesta] = []
    for p in candidatos:
        fecha_propuesta = random_date_between(p.fecha_registro, date.today())
        estado_prop = random.choices(
            ESTADOS_PROPUESTA,
            weights=[10, 70, 12, 8],  # mayoría 'Aceptada' por diseño
        )[0]
        prop = Propuesta(
            descripcion=(
                f"Suscripción Zimbra Collaboration Suite — "
                f"{fake.sentence(nb_words=10)}"
            ),
            fecha_propuesta=fecha_propuesta,
            estado=estado_prop,
            valor_estimado=Decimal(str(random.randint(500_000, 50_000_000))),
            id_prospecto=p.id_prospecto,
        )
        propuestas.append(prop)
    db.add_all(propuestas)
    db.flush()
    return propuestas


def seed_clientes_y_ventas(
    db, propuestas: list[Propuesta]
) -> tuple[list[Cliente], list[Venta]]:
    """
    Crea un cliente por cada prospecto cuya propuesta fue 'Aceptada',
    promueve ese prospecto a 'Convertido', y registra una venta por
    cada propuesta aceptada (UNIQUE id_propuesta).
    """
    aceptadas = [pr for pr in propuestas if pr.estado == "Aceptada"]

    # Agrupa por prospecto: un cliente por prospecto (UNIQUE id_prospecto).
    aceptadas_por_prospecto: dict[int, list[Propuesta]] = {}
    for pr in aceptadas:
        aceptadas_por_prospecto.setdefault(pr.id_prospecto, []).append(pr)

    # Crea clientes.
    clientes: list[Cliente] = []
    for id_prospecto in aceptadas_por_prospecto:
        prospecto = db.get(Prospecto, id_prospecto)
        prospecto.estado = "Convertido"
        c = Cliente(
            nombre=prospecto.nombre,
            correo=prospecto.correo,
            empresa=prospecto.empresa,
            telefono=prospecto.telefono,
            fecha_registro=date.today(),
            id_prospecto=id_prospecto,
            sync_salesforce=random.random() < 0.6,
            fecha_ult_sync=(
                datetime.now() - timedelta(days=random.randint(0, 30))
                if random.random() < 0.5
                else None
            ),
        )
        clientes.append(c)
    db.add_all(clientes)
    db.flush()

    # Mapa prospecto -> cliente para construir las ventas.
    pid_to_cid = {c.id_prospecto: c.id_cliente for c in clientes}

    ventas: list[Venta] = []
    for pr in aceptadas:
        cid = pid_to_cid.get(pr.id_prospecto)
        if cid is None:
            continue
        v = Venta(
            fecha_venta=pr.fecha_propuesta
            + timedelta(days=random.randint(1, 30)),
            monto=pr.valor_estimado,
            estado=random.choices(ESTADOS_VENTA, weights=[80, 15, 5])[0],
            metodo_pago=random.choice(METODOS_PAGO),
            id_propuesta=pr.id_propuesta,
            id_cliente=cid,
        )
        ventas.append(v)
    db.add_all(ventas)
    db.flush()
    return clientes, ventas


def seed_reportes(db, campanas: list[Campana], n: int = 30) -> list[Reporte]:
    reportes: list[Reporte] = []
    for _ in range(n):
        tipo = random.choice(TIPOS_REPORTE)
        fecha_gen = fake.date_time_between(start_date="-1y", end_date="now")
        periodo_inicio = random_date_between(
            date(2024, 6, 1), date.today() - timedelta(days=30)
        )
        periodo_fin = periodo_inicio + timedelta(days=random.randint(7, 90))

        resumen_por_tipo = {
            "Rendimiento Campana": (
                f"ROI: {random.randint(-50, 350)}% | "
                f"{random.randint(10, 100)} prospectos generados."
            ),
            "Prospectos Calificados": (
                f"Total: {random.randint(5, 50)} calificados en el periodo."
            ),
            "Ventas Periodo": (
                f"Ingresos: ${random.randint(1_000_000, 100_000_000):,} COP | "
                f"Ventas: {random.randint(1, 20)}."
            ),
            "Conversion Embudo": (
                f"Prospectos→Calificados: {random.randint(10, 40)}% | "
                f"Calificados→Clientes: {random.randint(20, 60)}%."
            ),
            "ROI Anual": (
                f"ROI anual acumulado: {random.randint(20, 250)}%."
            ),
        }

        r = Reporte(
            tipo_reporte=tipo,
            fecha_generacion=fecha_gen,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            resultado=resumen_por_tipo[tipo],
            id_campana=(
                random.choice(campanas).id_campana
                if random.random() < 0.7
                else None
            ),
        )
        reportes.append(r)
    db.add_all(reportes)
    db.flush()
    return reportes


# =====================================================================
#  Orquestador principal
# =====================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pobla la BD de Zimbra CRM con datos realistas."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra todos los datos antes de insertar (usa con cuidado).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Inserta aún si la BD ya tiene datos (puede fallar por UNIQUE).",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            print("⚠  Reseteando base de datos…")
            resetear_bd(db)
            print("   ✓ tablas vaciadas y AUTO_INCREMENT reiniciado.")
        elif ya_esta_seeded(db):
            if not args.force:
                print(
                    "⚠  La BD ya tiene >10 prospectos. Usa --reset para "
                    "reseed o --force para añadir."
                )
                return

        print("→  Sembrando CAMPAÑAS…")
        campanas = seed_campanas(db, n=30)
        print(f"   ✓ {len(campanas)} campañas")

        print("→  Sembrando PLANTILLAS DE COMUNICACIÓN…")
        plantillas = seed_plantillas(db, n=30)
        print(f"   ✓ {len(plantillas)} plantillas")

        print("→  Sembrando PROSPECTOS…")
        prospectos = seed_prospectos(db, campanas, n=60)
        print(f"   ✓ {len(prospectos)} prospectos")

        print("→  Sembrando INTERACCIONES DE MARKETING (recalcula scoring)…")
        interacciones = seed_interacciones(db, prospectos, campanas)
        print(f"   ✓ {len(interacciones)} interacciones")

        print("→  Sembrando COMUNICACIONES ENVIADAS…")
        comunicaciones = seed_comunicaciones(
            db, plantillas, prospectos, campanas, n=80
        )
        print(f"   ✓ {len(comunicaciones)} comunicaciones")

        print("→  Sembrando PROPUESTAS…")
        propuestas = seed_propuestas(db, prospectos, n=45)
        print(f"   ✓ {len(propuestas)} propuestas")

        print("→  Sembrando CLIENTES y VENTAS (a partir de aceptadas)…")
        clientes, ventas = seed_clientes_y_ventas(db, propuestas)
        print(f"   ✓ {len(clientes)} clientes, {len(ventas)} ventas")

        print("→  Sembrando REPORTES…")
        reportes = seed_reportes(db, campanas, n=30)
        print(f"   ✓ {len(reportes)} reportes")

        db.commit()
        print("\n✅  Seed completado.\n")

        # Resumen final ----------------------------------------------------
        print("Resumen de la BD:")
        tablas_resumen: list[tuple[str, type]] = [
            ("CAMPANA", Campana),
            ("PLANTILLA_COMUNICACION", PlantillaComunicacion),
            ("PROSPECTO", Prospecto),
            ("INTERACCION_MARKETING", InteraccionMarketing),
            ("COMUNICACION_ENVIADA", ComunicacionEnviada),
            ("PROPUESTA", Propuesta),
            ("CLIENTE", Cliente),
            ("VENTA", Venta),
            ("REPORTE", Reporte),
        ]
        for nombre, modelo in tablas_resumen:
            count = (
                db.scalar(select(func.count()).select_from(modelo)) or 0
            )
            print(f"  {nombre:25} {count:5d} registros")

    except Exception as e:
        db.rollback()
        print(f"\n❌  Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
