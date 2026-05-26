# Entregable — Sesión 2

**Proyecto integrador:** Sistema Transaccional Zimbra CRM
**Asignatura:** Sistemas Transaccionales de Bases de Datos
**Programa:** Ingeniería de Sistemas — Corporación Universitaria Minuto de Dios (UNIMINUTO Bogotá)
**Docente:** Ladi Paola Ballen Carrasco
**Fecha de entrega:** 19 de mayo de 2026

## Equipo

| Integrante | Rol principal en la sesión |
|---|---|
| **Hayder Esteban Barrera Pérez** | Modelo físico SQL · DDL · Inserts · Transacciones SQL |
| **Julian Mateo Artunduaga Gomez** | Backend Python · Servicios transaccionales · Endpoints |
| **Valery Tatiana Pamplona Gómez** | Frontend · Demos ACID · Documentación |

## 1. Objetivo de la sesión

Implementar el modelo relacional en MySQL, cargar datos simulados (mínimo 30 por tabla), programar transacciones ACID orientadas a operaciones reales del negocio y construir la conexión inicial del back-end con endpoints REST básicos.

## 2. Caso de negocio (recordatorio breve)

Zimbra Collaboration Suite (ZCS) opera un funnel comercial estándar: **Campaña → Prospecto → Interacciones (scoring) → Calificado → Propuesta → Aceptada → Cliente → Venta**. Sobre ese funnel se modelan las transacciones críticas que requieren garantías ACID (no se pueden quedar a la mitad: o todo se confirma, o todo se revierte).

## 3. Historias de usuario técnicas (HU-T) — Sesión 2

Estas historias técnicas complementan las HU-01 a HU-27 funcionales de la Sesión 1. Cada una tiene **responsable**, **criterios de aceptación** y **evidencia de implementación**.

### HU-T-01 — Implementación del modelo físico en MySQL
**Responsable:** Hayder Esteban Barrera Pérez

**Como** equipo de desarrollo, **quiero** materializar el modelo lógico de la Sesión 1 en 9 tablas MySQL con sus restricciones, **para que** la base de datos garantice integridad por sí misma.

**Criterios de aceptación:**
- [x] Las 9 tablas se crean con `CREATE TABLE` en un único script.
- [x] Todas las claves foráneas están declaradas.
- [x] Restricciones `CHECK` aplicadas: `fecha_fin >= fecha_inicio` en CAMPANA, `puntuacion >= 0` en PROSPECTO, `monto > 0` en VENTA, `valor_estimado >= 0` en PROPUESTA, `peso_scoring >= 0` en INTERACCION_MARKETING.
- [x] Restricciones `UNIQUE`: `correo` en PROSPECTO y CLIENTE, `id_prospecto` en CLIENTE, `id_propuesta` en VENTA.

**Evidencia:** `sql/zimbra_crm.sql` líneas 1-170.

### HU-T-02 — Carga de datos simulados (30+ por tabla)
**Responsable:** Hayder Esteban Barrera Pérez

**Como** estudiante de la sesión 2, **quiero** poblar las 9 tablas con datos coherentes, **para que** la profesora pueda evaluar el sistema con datos reales.

**Criterios de aceptación:**
- [x] Mínimo 30 registros por tabla.
- [x] Integridad referencial respetada (todo FK apunta a un registro existente).
- [x] Variedad de estados (no todos los prospectos en el mismo estado, etc.).
- [x] Coherencia: los prospectos con `propuesta.estado = 'Aceptada'` son los que tienen un cliente y una venta.

**Evidencia:** `sql/zimbra_crm.sql` líneas 170-440 (CAMPANA, PROSPECTO, INTERACCION_MARKETING, PLANTILLA_COMUNICACION, COMUNICACION_ENVIADA, PROPUESTA, CLIENTE, VENTA, REPORTE).

### HU-T-03 — Transacciones ACID a nivel SQL orientadas a negocio
**Responsable:** Hayder Esteban Barrera Pérez + Julian Mateo Artunduaga Gomez

**Como** equipo técnico, **quiero** implementar transacciones SQL que reproduzcan operaciones reales del CRM, **para que** queden demostradas las propiedades ACID dentro del contexto del negocio (no como ejemplos aislados).

**Criterios de aceptación:**
- [x] Cada transacción tiene una justificación de negocio explícita.
- [x] Se usan `START TRANSACTION`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` y `ROLLBACK TO`.
- [x] Al menos una transacción demuestra rollback parcial con SAVEPOINT.
- [x] Al menos una transacción demuestra rollback total.
- [x] Todas las transacciones están comentadas indicando qué propiedad ACID demuestran.

**Evidencia:** `sql/zimbra_crm.sql` líneas 450-700. Detalle en sección 5 de este documento.

### HU-T-04 — Conexión back-end a la base de datos
**Responsable:** Julian Mateo Artunduaga Gomez

**Como** desarrollador, **quiero** que el back-end se conecte a MySQL mediante SQLAlchemy con sesiones transaccionales explícitas, **para que** el control ACID se replique a nivel de aplicación.

**Criterios de aceptación:**
- [x] Configuración por variables de entorno (`.env`) con `python-dotenv`.
- [x] Engine SQLAlchemy con `autocommit=False`, `autoflush=False`, `pool_pre_ping=True`.
- [x] Dependencia `get_db()` por petición con cierre garantizado.
- [x] Endpoint `/api/health` para validar que la app responde.

**Evidencia:** [app/config.py](app/config.py), [app/database.py](app/database.py), [app/main.py](app/main.py).

### HU-T-05 — Modelos ORM y schemas de validación
**Responsable:** Julian Mateo Artunduaga Gomez

**Como** desarrollador, **quiero** mapear las 9 tablas a modelos SQLAlchemy 2.x y schemas Pydantic v2, **para que** la API tenga validación tipada de entrada/salida.

**Criterios de aceptación:**
- [x] Un archivo por entidad en `app/models/` con `Mapped`/`mapped_column`.
- [x] Relaciones bidireccionales con `back_populates`.
- [x] Schemas `Create`, `Update`, `Out` por entidad con tipos `Literal` para estados.

**Evidencia:** [app/models/](app/models/), [app/schemas/](app/schemas/).

### HU-T-06 — Endpoints REST básicos para las 9 entidades
**Responsable:** Julian Mateo Artunduaga Gomez

**Como** consumidor de la API, **quiero** endpoints CRUD para cada entidad, **para que** el frontend y herramientas de prueba (Swagger UI) puedan interactuar con el sistema.

**Criterios de aceptación:**
- [x] Para cada entidad: `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`.
- [x] Códigos HTTP correctos: 201 en POST, 204 en DELETE, 404 cuando no existe, 400/409 ante violaciones.
- [x] Swagger UI accesible en `/docs`.
- [x] Filtros útiles para el dashboard (`?estado=...`, `?id_prospecto=...`).

**Evidencia:** [app/routers/](app/routers/) — 9 archivos, ~50 endpoints documentados en `/docs`.

### HU-T-07 — Servicios transaccionales en el back-end
**Responsable:** Julian Mateo Artunduaga Gomez + Hayder Esteban Barrera Pérez

**Como** sistema, **quiero** replicar las transacciones de negocio en código Python usando SQLAlchemy con `with db.begin()`, `db.begin_nested()` (SAVEPOINTs), `commit()` y `rollback()`, **para que** las operaciones críticas mantengan ACID también desde la aplicación.

**Criterios de aceptación:**
- [x] `cerrar_venta()` ejecuta los 4 pasos del cierre dentro de una sola transacción con SAVEPOINT para creación de cliente (manejo de recompra).
- [x] `registrar_interaccion()` actualiza scoring y promueve estado atómicamente.
- [x] `marcar_inadecuado()` resetea puntuación + cambia estado en una transacción.
- [x] Cada función tiene docstring explicando las propiedades ACID demostradas.

**Evidencia:** [app/services/venta_service.py](app/services/venta_service.py), [app/services/scoring_service.py](app/services/scoring_service.py).

### HU-T-08 — Frontend para demostración interactiva
**Responsable:** Valery Tatiana Pamplona Gómez

**Como** equipo, **queremos** una interfaz web en HTML/CSS/JS vanilla, **para que** la sustentación incluya una demostración visual.

**Criterios de aceptación:**
- [x] Dashboard con métricas en vivo (consume `/api/reportes/conversion`).
- [x] Página de prospectos con filtros y modal para registrar interacción.
- [x] Página de ventas con flujo de cierre transaccional visible.
- [x] Cada modal de la app muestra el resultado de la transacción (COMMIT / ROLLBACK) sobre operaciones reales del CRM.

**Evidencia:** [frontend/index.html](frontend/index.html), [frontend/prospectos.html](frontend/prospectos.html), [frontend/ventas.html](frontend/ventas.html).

### HU-T-09 — Manual de ejecución y documentación
**Responsable:** Valery Tatiana Pamplona Gómez

**Como** docente o evaluador, **quiero** instrucciones claras para correr el sistema, **para que** pueda validarlo sin asistencia del equipo.

**Criterios de aceptación:**
- [x] README con instalación nativa y por Docker.
- [x] `docker-compose.yml` con MySQL + back-end + seed automático.
- [x] Sección de troubleshooting con los errores comunes.

**Evidencia:** [README.md](README.md), [docker-compose.yml](docker-compose.yml), [Dockerfile](Dockerfile).

## 4. Inventario de artefactos entregados

```
zimbra_crm/
├── sql/
│   └── zimbra_crm.sql              ← Script único: DDL + INSERTs + 7 transacciones
├── app/
│   ├── main.py                     ← FastAPI app
│   ├── config.py                   ← Variables de entorno
│   ├── database.py                 ← Engine + Session + get_db()
│   ├── models/                     ← 9 modelos SQLAlchemy
│   ├── schemas/                    ← Schemas Pydantic v2
│   ├── routers/                    ← 9 routers REST por entidad
│   └── services/                   ← Lógica con transacciones ACID
├── frontend/                       ← HTML + CSS + JS vanilla
├── scripts/
│   └── seed_database.py            ← Seed alternativo con Faker
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── README.md
└── ENTREGABLE_SESION_2.md          ← este documento
```

## 5. Transacciones ACID — diseño orientado a negocio

### 5.1 ¿Por qué transacciones de negocio?

Una transacción no debería ser un ejemplo artificial para "mostrar atomicidad". Debe modelar **una operación real e indivisible** del dominio: aquella que el negocio NO acepta a medias. Las propiedades ACID emergen naturalmente como consecuencia.

### 5.2 Las 7 transacciones SQL implementadas

| # | Transacción | Operación de negocio | Propiedades ACID |
|---|---|---|---|
| 1 | Onboarding de prospecto | Insertar prospecto + primera interacción | Atomicidad |
| 2 | Calificación automática | Insertar interacción + sumar scoring + promover estado | Atomicidad + Consistencia |
| 3 | Generar propuesta | Crear oferta comercial para prospecto calificado | Atomicidad + Durabilidad |
| 4 | **Cierre de venta** (con SAVEPOINT) | Aceptar propuesta + crear cliente + convertir prospecto + registrar venta | Atomicidad + Consistencia + Durabilidad |
| 5 | Descalificar prospecto | Cambiar estado a Inadecuado + reset puntuación | Atomicidad |
| 6 | **ROLLBACK TO SAVEPOINT** | Corregir error de atribución sin perder calificación | Atomicidad parcial |
| 7 | ROLLBACK total | Rechazar propuesta a prospecto Inadecuado por regla de negocio | Atomicidad |

### 5.3 Detalle de la transacción estrella: cierre de venta

```sql
START TRANSACTION;
  -- 1) Aceptar propuesta
  UPDATE PROPUESTA SET estado = 'Aceptada' WHERE id_propuesta = @nueva_propuesta;

  -- 2) Crear cliente desde prospecto (SAVEPOINT por caso recompra)
  SAVEPOINT sp_crear_cliente;
  INSERT INTO CLIENTE (...) SELECT ... FROM PROSPECTO WHERE id_prospecto = @nuevo_prospecto;

  -- 3) Marcar prospecto como Convertido
  UPDATE PROSPECTO SET estado = 'Convertido' WHERE id_prospecto = @nuevo_prospecto;

  -- 4) Registrar la venta
  INSERT INTO VENTA (...) SELECT ... FROM PROPUESTA WHERE id_propuesta = @nueva_propuesta;
COMMIT;
```

Si cualquier paso falla, MySQL hace ROLLBACK automático y ninguna escritura persiste. El SAVEPOINT `sp_crear_cliente` permite manejar el caso de recompra (cliente ya existe) sin abortar la transacción completa.

### 5.4 Transacciones a nivel back-end (mismo flujo, lenguaje Python)

| Endpoint | Función Python | Archivo |
|---|---|---|
| `POST /api/ventas/cerrar-venta` | `cerrar_venta()` | [app/services/venta_service.py](app/services/venta_service.py) |
| `POST /api/interacciones/registrar` | `registrar_interaccion()` | [app/services/scoring_service.py](app/services/scoring_service.py) |
| `POST /api/prospectos/{id}/marcar-inadecuado` | `marcar_inadecuado()` | [app/services/scoring_service.py](app/services/scoring_service.py) |

### 5.5 Aislamiento y durabilidad — configuración del motor

Las propiedades de aislamiento y durabilidad NO se demuestran con endpoints artificiales, sino con la propia configuración de InnoDB y las operaciones reales del CRM:

| Propiedad | Cómo se garantiza |
|---|---|
| Aislamiento | InnoDB usa `REPEATABLE READ` por defecto. Dos transacciones `cerrar-venta` concurrentes sobre la misma propuesta no pueden completar ambas porque `VENTA.id_propuesta` es UNIQUE. |
| Durabilidad | `innodb_flush_log_at_trx_commit = 1` (default): cada COMMIT escribe al redo log antes de retornar. Los cambios sobreviven a un reinicio del servidor. |

## 6. Conexión back-end ↔ base de datos

**Stack:** Python 3.11 + FastAPI 0.115 + SQLAlchemy 2.x + PyMySQL.

**Configuración clave** ([app/database.py](app/database.py)):

```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,       # transacciones explícitas
    autoflush=False,        # control explícito de flushes
    expire_on_commit=False,
)
```

Cada petición HTTP recibe una `Session` viva vía `Depends(get_db)`, que se cierra al terminar. Las transacciones se abren con `with db.begin():` en los servicios; los SAVEPOINTs se abren con `db.begin_nested()`.

## 7. Manual de ejecución

### Opción A — Docker (recomendado)

```bash
cd zimbra_crm
cp .env.example .env
docker compose up --build
```

Abrir http://localhost:8000 (frontend) y http://localhost:8000/docs (Swagger).

### Opción B — Instalación nativa

```bash
mysql -u root -p < sql/zimbra_crm.sql
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar DB_PASSWORD
uvicorn app.main:app --reload
```

## 8. Plan de sustentación

| Paso | Qué mostrar | Quién |
|---|---|---|
| 1 | Diagrama del modelo relacional (recordar Sesión 1) | Hayder |
| 2 | Abrir `sql/zimbra_crm.sql` y mostrar el DDL + 30+ inserts por tabla | Hayder |
| 3 | Ejecutar el script en MySQL Workbench y mostrar conteos por tabla | Hayder |
| 4 | Explicar las 7 transacciones SQL, especialmente la T4 (cierre de venta con SAVEPOINT) y T6 (ROLLBACK TO SAVEPOINT) | Hayder |
| 5 | Arrancar el back-end (`docker compose up` o `uvicorn`) | Julian |
| 6 | Abrir Swagger UI en `/docs` y mostrar los ~50 endpoints organizados por tag | Julian |
| 7 | Probar el endpoint transaccional `POST /api/ventas/cerrar-venta` desde Swagger y mostrar la respuesta | Julian |
| 8 | Abrir el frontend en http://localhost:8000 — recorrer Dashboard, Prospectos, Ventas | Valery |
| 9 | Registrar interacciones en un prospecto Pendiente hasta cruzar el umbral y verlo promoverse a Calificado | Valery |
| 10 | Cerrar una venta desde la UI y mostrar el resultado de la transacción (COMMIT) en el modal | Valery |
| 11 | Cierre: mostrar este documento `ENTREGABLE_SESION_2.md` como índice del entregable | Equipo |

## 9. Verificación contra el checklist del entregable

| Requisito del enunciado | Estado | Evidencia |
|---|---|---|
| Implementación del modelo en SQL (`CREATE TABLE`) | ✅ | `sql/zimbra_crm.sql` líneas 16-170 |
| Inserción de datos simulados (mínimo 30 por tabla) | ✅ | 30 registros por cada una de las 9 tablas |
| `BEGIN TRANSACTION` (= `START TRANSACTION`) | ✅ | 7 ocurrencias en las transacciones |
| `COMMIT` | ✅ | 6 ocurrencias (T1, T2, T3, T4, T5, T6) |
| `ROLLBACK` | ✅ | T7 (rollback total) |
| Uso de `SAVEPOINT` | ✅ | T4 (`sp_crear_cliente`), T6 (`sp_antes_interaccion`) |
| Simulación de errores y recuperación | ✅ | T6 (ROLLBACK TO SAVEPOINT), T7 (ROLLBACK por regla de negocio), `cerrar-venta` con SAVEPOINT para recompra |
| Conexión inicial del back-end a la BD | ✅ | `app/database.py`, `app/main.py`, endpoint `/api/health` |
| Endpoints básicos | ✅ | ~50 endpoints en `/docs` (Swagger UI) |
| Historias de usuario con criterios de aceptación y responsable | ✅ | Sección 3 de este documento (HU-T-01 a HU-T-09) |
| Script SQL con tablas, datos y transacciones | ✅ | `sql/zimbra_crm.sql` (único archivo) |
| Código inicial del back-end con conexión a BD | ✅ | Carpeta `app/` |

---

**Firma del equipo:**
Hayder Esteban Barrera Pérez · Julian Mateo Artunduaga Gomez · Valery Tatiana Pamplona Gómez
UNIMINUTO — Ingeniería de Sistemas — 2026