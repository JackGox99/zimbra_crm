# Zimbra CRM — Sistema Transaccional

Aplicación web que simula los procesos de marketing y ventas de **Zimbra
Collaboration Suite (ZCS)** y demuestra explícitamente las cuatro
propiedades **ACID** (Atomicidad · Consistencia · Aislamiento ·
Durabilidad) sobre MySQL 8.

Es el entregable de la **Sesión 2** del proyecto integrador de la
asignatura *Sistemas Transaccionales de Bases de Datos* (UNIMINUTO).

## Equipo

- **Hayder Esteban Barrera Pérez**
- **Julian Mateo Artunduaga Gomez**
- **Valery Tatiana Pamplona Gómez**

**Docente:** Ladi Paola Ballen Carrasco
**Asignatura:** Sistemas Transaccionales de Bases de Datos
**Institución:** Corporación Universitaria Minuto de Dios — Bogotá

## Caso de estudio: Zimbra

Zimbra es una empresa de software de código abierto cuyo producto
estrella es **Zimbra Collaboration Suite (ZCS)**: una plataforma de
correo, calendario y colaboración usada por miles de empresas. Su
modelo comercial combina marketing digital, periodo de prueba gratuito
de 60 días, propuestas comerciales personalizadas y conversión a
cliente con suscripción anual.

Este sistema implementa ese flujo end-to-end como un CRM transaccional:

```
   Campaña → Prospecto → (Interacciones que suben puntuación)
       → Prospecto Calificado → Propuesta → Aceptada
       → Cliente → Venta → Cliente sincronizado con Salesforce
```

## Stack técnico

| Capa | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.11+ |
| Framework backend | FastAPI | 0.115.6 |
| ORM | SQLAlchemy (sintaxis 2.x moderna) | 2.0.36 |
| Driver MySQL | PyMySQL + cryptography | 1.1.1 / 44.0.0 |
| Validación | Pydantic v2 + email-validator | 2.10.4 / 2.2.0 |
| Variables de entorno | python-dotenv | 1.0.1 |
| Generación de datos | Faker (locale es_CO) | 33.1.0 |
| Servidor ASGI | Uvicorn | 0.34.0 |
| Frontend | HTML + CSS + JavaScript vanilla | — |
| Base de datos | MySQL | 8.4 |
| Documentación API | Swagger UI (nativo de FastAPI) | — |

**Sin Docker. Sin Alembic. Sin JWT. Sin tests automatizados.** Simplicidad.

## Estructura del proyecto

```
zimbra_crm/
├── app/
│   ├── main.py                    # FastAPI app + CORS + montaje del frontend
│   ├── config.py                  # carga .env tipada
│   ├── database.py                # engine, SessionLocal, Base, get_db()
│   ├── models/                    # 9 modelos SQLAlchemy 2.x
│   │   ├── campana.py
│   │   ├── prospecto.py
│   │   ├── interaccion_marketing.py
│   │   ├── plantilla_comunicacion.py
│   │   ├── comunicacion_enviada.py
│   │   ├── propuesta.py
│   │   ├── cliente.py
│   │   ├── venta.py
│   │   └── reporte.py
│   ├── schemas/                   # Pydantic v2 (Create / Update / Out)
│   ├── routers/                   # Routers REST agrupados por entidad
│   │   ├── campanas.py            # CRUD
│   │   ├── prospectos.py          # CRUD + /pruebas-por-vencer + /marcar-inadecuado
│   │   ├── interacciones.py       # CRUD + /registrar (transaccional)
│   │   ├── propuestas.py          # CRUD
│   │   ├── clientes.py            # CRUD
│   │   ├── ventas.py              # CRUD + /cerrar-venta (3 SAVEPOINTs)
│   │   ├── comunicaciones.py      # CRUD plantillas + envíos
│   │   ├── reportes.py            # CRUD + /conversion + /campanas/{id}/rendimiento
│   │   └── automatizacion.py      # SP / UDF / auditoría (Sesión 3)
│   └── services/                  # Lógica con transacciones explícitas
│       ├── venta_service.py       # cerrar_venta(): BEGIN + 3 SP + COMMIT
│       └── scoring_service.py     # registrar_interaccion(), marcar_inadecuado()
├── frontend/
│   ├── index.html                 # Dashboard con tarjetas + embudo
│   ├── prospectos.html            # Tabla filtrable + modal de interacción
│   ├── ventas.html                # Propuestas + cierre transaccional
│   ├── automatizacion.html        # Triggers / SP / UDF en acción
│   ├── css/style.css
│   └── js/{api,index,prospectos,ventas,automatizacion}.js
├── scripts/
│   └── seed_database.py           # Inserta 30+ registros por tabla con Faker
├── sql/
│   └── zimbra_crm.sql             # Script único: 9 tablas + datos + transacciones +
│                                  # triggers + procedimientos + UDFs (3 entregas)
├── presentacion.html              # Sustentación standalone (las 3 entregas)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Cómo ejecutar

### Opción A — Con Docker (más rápido)

Requisitos: **Docker Engine + Docker Compose v2**.

```bash
cd zimbra_crm
cp .env.example .env                # editar DB_PASSWORD si querés
docker compose up --build
```

Esto arranca tres servicios: `db` (MySQL 8.4 con el DDL precargado),
`web` (FastAPI con hot-reload en http://localhost:8000) y `seed`
(contenedor one-shot que puebla la BD con 30+ registros por tabla).

Comandos útiles:

```bash
docker compose logs -f web                              # ver logs del backend
docker compose exec web bash                            # shell dentro del contenedor
docker compose exec db mysql -uroot -p zimbra_crm       # consola MySQL
docker compose run --rm seed --reset                    # forzar re-seed
docker compose down                                     # parar contenedores
docker compose down -v                                  # parar + borrar el volumen MySQL
```

Una vez arriba, abrí http://localhost:8000 y http://localhost:8000/docs.

### Opción B — Instalación nativa

Requisitos previos:

- Python **3.11 o superior**.
- MySQL **8.0+** (probado con 8.4) corriendo localmente.
- Usuario de MySQL con permisos para crear bases de datos.

### Pasos

**1. Clonar / descargar el proyecto** y entrar al directorio:

```bash
cd zimbra_crm
```

**2. Crear la base de datos** y el esquema con datos iniciales:

```bash
mysql -u root -p < sql/zimbra_crm.sql
```

Esto crea la base `zimbra_crm` con las 9 tablas, sus FK, CHECKs y un
mínimo de datos de ejemplo.

**3. Crear el entorno virtual e instalar dependencias:**

```bash
python3 -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configurar variables de entorno:**

```bash
cp .env.example .env
```

Editar `.env` y poner la contraseña real de MySQL:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_real_aqui
DB_NAME=zimbra_crm
API_HOST=127.0.0.1
API_PORT=8000
```

**5. Poblar la base de datos con datos realistas** (30+ por tabla):

```bash
python scripts/seed_database.py --reset
```

Salida esperada:
```
⚠  Reseteando base de datos…
   ✓ tablas vaciadas y AUTO_INCREMENT reiniciado.
→  Sembrando CAMPAÑAS…
   ✓ 30 campañas
→  Sembrando PLANTILLAS DE COMUNICACIÓN…
   ✓ 30 plantillas
→  Sembrando PROSPECTOS…
   ✓ 60 prospectos
→  Sembrando INTERACCIONES DE MARKETING (recalcula scoring)…
   ✓ ~250 interacciones
...
✅  Seed completado.
```

**6. Iniciar el servidor:**

```bash
uvicorn app.main:app --reload
```

**7. Abrir en el navegador:**

- **Aplicación web:** http://localhost:8000
- **Swagger UI (API):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Demostración de propiedades ACID

Las propiedades ACID se manifiestan en **operaciones reales del negocio**
(no en demos artificiales). Cada caso corresponde a una transacción del
script SQL o a un endpoint transaccional del backend:

| Propiedad | Dónde se demuestra | Qué pasa |
|---|---|---|
| **Atomicidad** | `POST /api/ventas/cerrar-venta` | Aceptar propuesta + crear cliente + convertir prospecto + registrar venta deben ocurrir todas o ninguna. |
| **Atomicidad parcial** | SAVEPOINTs anidados en `cerrar-venta` | Si la creación del cliente falla por UNIQUE (recompra), se hace `ROLLBACK TO sp2`, se recupera el cliente y la venta continúa. |
| **Consistencia** | CHECKs y FKs del DDL + reglas en triggers | `monto > 0`, `valor_estimado >= 0`, FKs cliente/propuesta, promoción a `Calificado` sólo desde estados promovibles. |
| **Aislamiento** | InnoDB con nivel `REPEATABLE READ` | Dos transacciones concurrentes en `cerrar-venta` no pueden duplicar la venta porque `id_propuesta` es UNIQUE. |
| **Durabilidad** | `innodb_flush_log_at_trx_commit=1` | Tras `COMMIT`, los cambios sobreviven a un reinicio del servidor. |

### Endpoint transaccional principal: cerrar venta

`POST /api/ventas/cerrar-venta` ejecuta el flujo completo:

```
BEGIN
  ├── (carga propuesta + validaciones)
  ├── SAVEPOINT sp1
  │     UPDATE PROPUESTA SET estado = 'Aceptada' WHERE id = ?
  ├── RELEASE SAVEPOINT sp1
  ├── SAVEPOINT sp2
  │     INSERT INTO CLIENTE (...)
  │     ┌─ si UNIQUE conflict (cliente ya existe):
  │     │    ROLLBACK TO sp2
  │     │    SELECT cliente existente
  │     └─ sino: RELEASE SAVEPOINT sp2
  ├── SAVEPOINT sp3
  │     UPDATE PROSPECTO SET estado = 'Convertido'
  │     INSERT INTO VENTA (...)
  ├── RELEASE SAVEPOINT sp3
COMMIT
```

Si **cualquier paso** falla irrecuperablemente, la transacción completa
se revierte y nada queda persistido — Atomicidad demostrada.

## Automatización (Sesión 3)

La parte final de `sql/zimbra_crm.sql` agrega lógica avanzada integrada
al flujo del CRM **sin crear tablas nuevas** (reutiliza las 9 tablas
originales):

- **4 triggers** que disparan reglas de negocio al insertar/actualizar
  (scoring de interacción, propuesta aceptada → prospecto convertido,
  inadecuado → puntuación 0, bitácora de cambios de estado en `REPORTE`).
- **3 procedimientos almacenados**: reporte mensual de ventas, extensión
  de trial y limpieza de trials vencidos.
- **3 funciones UDF**: nivel de interés, días restantes de trial y
  lifetime value del cliente.

La página `frontend/automatizacion.html` consume todo esto desde botones
y lee de la tabla `REPORTE` (filtrada por `tipo_reporte='Auditoria
Estado Prospecto'`) la bitácora que pobla el trigger de auditoría.

## Mapa de endpoints

### CRUD básico (las 9 entidades)

| Recurso | URL base |
|---|---|
| Campañas | `/api/campanas/` |
| Prospectos | `/api/prospectos/` |
| Interacciones | `/api/interacciones/` |
| Propuestas | `/api/propuestas/` |
| Clientes | `/api/clientes/` |
| Ventas | `/api/ventas/` |
| Plantillas | `/api/plantillas/` |
| Comunicaciones | `/api/comunicaciones/` |
| Reportes | `/api/reportes/` |

Cada uno con: `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`.

### Endpoints transaccionales (con ACID explícita)

| Método | Endpoint | Propiedades ACID |
|---|---|---|
| POST | `/api/ventas/cerrar-venta` | Atomicidad + Consistencia + Durabilidad (3 SAVEPOINTs) |
| POST | `/api/interacciones/registrar` | Atomicidad (insert + update + promoción) |
| POST | `/api/prospectos/{id}/marcar-inadecuado` | Atomicidad (estado + puntuación) |

### Endpoints consultivos

| Método | Endpoint | Para qué |
|---|---|---|
| GET | `/api/reportes/conversion` | Embudo total prospectos → clientes |
| GET | `/api/reportes/campanas/{id}/rendimiento` | ROI de una campaña |
| GET | `/api/prospectos/pruebas-por-vencer?dias=N` | Trial vence en N días (RF-008) |

### Automatización (Sesión 3)

| Método | Endpoint | Objeto invocado |
|---|---|---|
| POST | `/api/automatizacion/reporte-mensual` | `CALL sp_reporte_mensual_ventas(anio, mes)` |
| POST | `/api/automatizacion/extender-trial/{id}?dias=N` | `CALL sp_extender_trial(id, dias)` |
| POST | `/api/automatizacion/limpiar-trials-vencidos` | `CALL sp_marcar_trials_vencidos()` |
| GET  | `/api/automatizacion/funciones/nivel-interes?puntuacion=N` | `SELECT fn_nivel_interes(N)` |
| GET  | `/api/automatizacion/funciones/dias-restantes/{id}` | `SELECT fn_dias_restantes_trial(id)` |
| GET  | `/api/automatizacion/funciones/lifetime-value/{id}` | `SELECT fn_lifetime_value(id)` |
| GET  | `/api/automatizacion/auditoria` | Lee la tabla poblada por `trg_audit_estado_prospecto` |

## Cómo sustentar la entrega

Guion sugerido para la presentación frente a la docente:

1. **Mostrar el caso de estudio** (este README, sección "Caso de estudio").

2. **Iniciar el sistema** con `uvicorn app.main:app --reload` y abrir
   http://localhost:8000.

3. **Recorrer el dashboard** (`index.html`) mostrando las métricas reales
   provenientes de las consultas agregadas en `/api/reportes/conversion`.

4. **Mostrar Swagger UI** (http://localhost:8000/docs) — todos los
   endpoints documentados automáticamente, agrupados por tag.

5. **Demostrar el flujo de scoring transaccional**:
   - Ir a `prospectos.html`, filtrar por estado `Pendiente`.
   - Elegir un prospecto con puntuación baja.
   - Click en `+ Interacción` → seleccionar `Descarga Prueba (+10)`.
   - Repetir hasta cruzar el umbral de 15: el modal mostrará el mensaje
     `🎉 Prospecto promovido a Calificado`.

6. **Demostrar el cierre de venta con SAVEPOINTs**:
   - Ir a `ventas.html`, elegir una propuesta pendiente.
   - Click en `Cerrar venta` → seleccionar método de pago → confirmar.
   - El modal muestra si fue un cliente nuevo o reutilizado (caso recompra).
   - La tabla de "Ventas registradas" se actualiza automáticamente.

7. **Ir a la página `automatizacion.html`** (Sesión 3):
   - Generar un reporte mensual (`CALL sp_reporte_mensual_ventas`).
   - Consultar las UDFs (nivel de interés, días restantes, LTV).
   - Revisar la **bitácora poblada por el trigger** de auditoría.

8. **Abrir `presentacion.html`** (archivo standalone en la raíz del
   proyecto) para acompañar la sustentación con diapositivas
   divididas por entrega.

9. **Mostrar el código** de un servicio transaccional clave:
   [app/services/venta_service.py](app/services/venta_service.py) —
   el docstring del módulo explica las 4 propiedades ACID y cada SAVEPOINT
   está comentado en español.

## Requerimientos funcionales cubiertos (Sesión 1)

| RF | Descripción | Cubierto por |
|---|---|---|
| RF-001 | Rastreo automatizado de interacciones | `INTERACCION_MARKETING` + `POST /api/interacciones/registrar` |
| RF-002 | Gestión CRUD de campañas | `/api/campanas/*` |
| RF-003 | Calificación automatizada por scoring | `scoring_service.registrar_interaccion()` con umbral 15 |
| RF-004 | Alertas para prospectos calificados | Respuesta `prospecto_calificado_ahora` del endpoint |
| RF-005 | Envío de comunicaciones automatizadas | `PLANTILLA_COMUNICACION` + `COMUNICACION_ENVIADA` |
| RF-006 | Gestión de propuestas comerciales | `/api/propuestas/*` |
| RF-007 | Registro de ventas con conversión a cliente | `POST /api/ventas/cerrar-venta` (transaccional) |
| RF-008 | Monitoreo del periodo de prueba de 60 días | `GET /api/prospectos/pruebas-por-vencer?dias=N` |
| RF-009 | Sincronización con Salesforce | Flag `sync_salesforce` + `fecha_ult_sync` en `CLIENTE` |
| RF-010 | Generación de reportes parametrizados | `/api/reportes/conversion`, `/rendimiento`, `REPORTE` |
| RF-011 | Filtrado de prospectos no calificados | `GET /api/prospectos/?estado=Inadecuado` |

## Troubleshooting

### `ImportError: email-validator is not installed`
Asegúrate de que se instalaron todas las dependencias:
```bash
pip install -r requirements.txt
```

### `pymysql.err.OperationalError: (1045, "Access denied for user ...")`
La contraseña en `.env` es incorrecta. Verifica el `DB_PASSWORD`.

### `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`
MySQL no está corriendo o el puerto es distinto:
```bash
sudo systemctl status mysqld     # En Fedora/RHEL
sudo systemctl start mysqld
```

### `RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods`
MySQL 8 usa `caching_sha2_password` por defecto. Ya está en
`requirements.txt`:
```bash
pip install cryptography
```

### `sqlalchemy.exc.OperationalError: (1146, "Table 'zimbra_crm.X' doesn't exist")`
Primero hay que crear las tablas:
```bash
mysql -u root -p < sql/zimbra_crm.sql
```

### `IntegrityError: Duplicate entry ... for key 'correo'`
La BD ya tiene datos del seed previo. Reinicia con:
```bash
python scripts/seed_database.py --reset
```

### Puerto 8000 ocupado
Cambia `API_PORT` en `.env` o arranca uvicorn con `--port 8080`:
```bash
uvicorn app.main:app --reload --port 8080
```

### El frontend no carga estilos / JS
Verifica que la app esté sirviendo `/css/style.css` y `/js/*.js`. Si no,
revisa que `frontend/` exista en el path correcto y que `main.py` lo
esté montando como `StaticFiles`.

## Licencia

Trabajo académico — UNIMINUTO, 2026.
