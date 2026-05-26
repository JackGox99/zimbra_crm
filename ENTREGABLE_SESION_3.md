# Corporación Universitaria Minuto de Dios — UNIMINUTO

**Programa de Ingeniería de Sistemas**
**Sistemas Transaccionales de Bases de Datos**

# Sistema Transaccional Zimbra CRM
## Sesión 3 — Automatización y Lógica Avanzada
### Triggers, Procedimientos Almacenados, Funciones UDF y Front-end Conectado

**Integrantes:**
Hayder Esteban Barrera Pérez
Julian Mateo Artunduaga Gomez
Valery Tatiana Pamplona Gómez

**Docente:** Ladi Paola Ballen Carrasco
**Fecha:** 25 de mayo de 2026

---

## Tabla de Contenido

1. Resumen ejecutivo
2. Entregables de la sesión
3. Historias de usuario
   - 3.1 Módulo 10 — Triggers de negocio
   - 3.2 Módulo 11 — Procedimientos almacenados
   - 3.3 Módulo 12 — Funciones UDF
   - 3.4 Módulo 13 — Front-end conectado
4. Script SQL (sección Sesión 3 de `zimbra_crm.sql`)
   - 4.1 Decisión de diseño: usar las 9 tablas originales
   - 4.2 Triggers implementados
   - 4.3 Procedimientos almacenados
   - 4.4 Funciones UDF
   - 4.5 Refresco de fechas de prueba
5. Back-end con endpoints funcionales
   - 5.1 Nuevo router `automatizacion`
   - 5.2 Ajuste del servicio de scoring (delegación en trigger)
   - 5.3 Validación vía Swagger
6. Front-end CONECTADO
   - 6.1 Página `automatizacion.html`
   - 6.2 Página `datos.html` — Explorador de las 9 tablas
   - 6.3 Botón "Extender trial" en la página de Prospectos
   - 6.4 Actualización del flujo de scoring
7. Manual de ejecución
8. Cierre

---

## 1. Resumen ejecutivo

La presente entrega complementa la base transaccional de la Sesión 2 con **lógica avanzada que vive en la base de datos**: cuatro triggers integrados al flujo del CRM, tres procedimientos almacenados con sentido de negocio, tres funciones UDF para cálculos centralizados y un front-end completamente conectado a todos estos objetos. La premisa de diseño fue NO crear tablas adicionales: toda la nueva funcionalidad se construye sobre las nueve tablas originales del modelo, reutilizando especialmente la tabla `REPORTE` como bitácora del trigger de auditoría.

El resultado es un sistema en el que la aplicación deja de duplicar la lógica del negocio en Python: el cálculo del scoring, la promoción a `Calificado`, la conversión automática al aceptar una propuesta y la auditoría del estado del prospecto ahora son responsabilidad de la base de datos. El back-end solo orquesta y el front-end solo presenta — la regla siempre se cumple, incluso si la interacción se inserta desde Swagger, desde un cliente SQL o desde otro trigger en cadena.

---

## 2. Entregables de la sesión

| Producto | Archivo | Contenido |
|---|---|---|
| 1. Script SQL con triggers, procedimientos y funciones | `sql/zimbra_crm.sql` (sección final) | DDL adicional de Sesión 3 integrado al final del script único de la BD: 4 triggers, 3 SPs, 3 UDFs y los UPDATEs que refrescan las fechas de prueba. |
| 2. Back-end con endpoints funcionales | `app/routers/automatizacion.py`, `app/schemas/automatizacion.py`, `app/services/scoring_service.py` (actualizado) | Router nuevo con 7 endpoints que invocan SPs, UDFs y consultan la bitácora poblada por el trigger de auditoría. |
| 3. Front-end CONECTADO | `frontend/automatizacion.html`, `frontend/datos.html`, `frontend/js/automatizacion.js`, `frontend/js/datos.js`, `frontend/js/prospectos.js` (actualizado) | Página de automatización, explorador de las 9 tablas, botón "Extender trial" en la tarjeta del prospecto. |
| 4. Historias de usuario | Este documento — Sección 3 | 13 historias agrupadas en 4 módulos nuevos, con criterios de aceptación verificables y responsable por integrante. |

---

## 3. Historias de usuario

Las 13 historias de la Sesión 3 continúan la numeración de la Sesión 2 (que cerró en HU-27). Cada una describe una funcionalidad nueva implementada en triggers, procedimientos, funciones o en el front-end conectado.

### 3.1 Módulo 10 — Triggers de negocio
**Responsable del módulo:** Valery Tatiana Pamplona Gómez

| HU-28 | Historia de Usuario |
|---|---|
| **Descripción** | Como gerente comercial, quiero que cada interacción de marketing actualice el scoring del prospecto y lo promueva a `Calificado` cuando cruce el umbral, sin necesidad de que la aplicación recalcule nada manualmente. |
| **Criterios de aceptación** | • El trigger `trg_interaccion_actualiza_scoring` (AFTER INSERT en `INTERACCION_MARKETING`) suma `peso_scoring` al campo `puntuacion` del prospecto.<br>• Si la nueva puntuación supera 15 y el estado actual es `Pendiente` o `Contactado`, el trigger lo actualiza a `Calificado` en la misma transacción.<br>• La regla se cumple aunque la inserción se haga desde Swagger, desde un cliente MySQL o desde otra rutina. |
| **Responsable** | Valery Tatiana Pamplona Gómez |

| HU-29 | Historia de Usuario |
|---|---|
| **Descripción** | Como ejecutivo de ventas, quiero que aceptar una propuesta marque automáticamente al prospecto como `Convertido`, sin depender del backend. |
| **Criterios de aceptación** | • El trigger `trg_propuesta_aceptada_promueve_prospecto` (AFTER UPDATE en `PROPUESTA`) detecta el cambio a estado `Aceptada` y promueve al prospecto a `Convertido`.<br>• La regla cumple el ejemplo del enunciado de la Sesión 3: *"actualizar estado de propuesta"*.<br>• El trigger no actúa si el prospecto ya era `Convertido`, evitando rescritura innecesaria. |
| **Responsable** | Valery Tatiana Pamplona Gómez |

| HU-30 | Historia de Usuario |
|---|---|
| **Descripción** | Como gerente de marketing, quiero que al marcar un prospecto como `Inadecuado` su puntuación quede en 0 a nivel de base de datos, para evitar que aparezca en alertas con scoring residual. |
| **Criterios de aceptación** | • El trigger `trg_prospecto_inadecuado_resetea_score` (BEFORE UPDATE en `PROSPECTO`) detecta el cambio de estado a `Inadecuado` y fuerza `NEW.puntuacion = 0`.<br>• La regla se cumple aunque la aplicación no resetee la puntuación explícitamente.<br>• El reset solo ocurre cuando el estado **cambia** a `Inadecuado` (no si ya lo era). |
| **Responsable** | Hayder Esteban Barrera Pérez |

| HU-31 | Historia de Usuario |
|---|---|
| **Descripción** | Como auditor, quiero que cada cambio de estado de un prospecto quede registrado automáticamente con su estado anterior, el nuevo y la puntuación, para tener trazabilidad sin requerir intervención de la aplicación. |
| **Criterios de aceptación** | • El trigger `trg_audit_estado_prospecto` (AFTER UPDATE en `PROSPECTO`) inserta una fila en la tabla `REPORTE` cada vez que el estado cambia.<br>• El registro usa `tipo_reporte = 'Auditoria Estado Prospecto'` y serializa los datos del cambio como JSON en el campo `resultado` (`JSON_OBJECT`).<br>• La aplicación **solo lee** la bitácora (endpoint `/api/automatizacion/auditoria`); nunca escribe directamente. La fuente de verdad es el trigger.<br>• La bitácora se mantiene en una tabla ya existente del modelo (`REPORTE`), respetando la decisión de no crear tablas nuevas. |
| **Responsable** | Hayder Esteban Barrera Pérez |

### 3.2 Módulo 11 — Procedimientos almacenados
**Responsable del módulo:** Julian Mateo Artunduaga Gomez

| HU-32 | Historia de Usuario |
|---|---|
| **Descripción** | Como gerente comercial, quiero ejecutar el cierre mensual de ventas con un solo procedimiento que totalice las ventas pagadas del mes, identifique la campaña con mayor facturación y persista el reporte. |
| **Criterios de aceptación** | • El SP `sp_reporte_mensual_ventas(p_anio, p_mes)` calcula `SUM(monto)` y `COUNT(*)` de ventas pagadas en el rango `[YYYY-MM-01, LAST_DAY)`.<br>• Identifica la campaña con mayor facturación uniendo `VENTA` → `CLIENTE` → `PROSPECTO` → `CAMPANA`.<br>• Inserta el reporte resultante en la tabla `REPORTE` con `tipo_reporte = 'Ventas Periodo (SP)'`.<br>• Valida que `p_mes` esté entre 1 y 12; en caso contrario lanza `SIGNAL SQLSTATE '45000'` con mensaje legible.<br>• Está expuesto en el endpoint `POST /api/automatizacion/reporte-mensual` y disponible desde la página de Automatización. |
| **Responsable** | Julian Mateo Artunduaga Gomez |

| HU-33 | Historia de Usuario |
|---|---|
| **Descripción** | Como comercial, quiero extender el periodo de prueba de un prospecto prometedor con una sola llamada, con validaciones de negocio en la base de datos. |
| **Criterios de aceptación** | • El SP `sp_extender_trial(p_id_prospecto, p_dias)` valida que el prospecto tenga `fecha_fin_prueba IS NOT NULL` antes de actualizar.<br>• Rechaza extensiones fuera del rango `[1, 90]` con `SIGNAL SQLSTATE '45000'`.<br>• Suma `p_dias` a `fecha_fin_prueba` y devuelve el resumen del cambio.<br>• Está expuesto en `POST /api/automatizacion/extender-trial/{id}?dias=N` y disponible desde el botón "⏰ Extender trial" en la tarjeta del prospecto. |
| **Responsable** | Julian Mateo Artunduaga Gomez |

| HU-34 | Historia de Usuario |
|---|---|
| **Descripción** | Como operador del sistema, quiero ejecutar una limpieza periódica que marque como `Inadecuado` a los prospectos cuyo trial venció y no convirtieron en clientes. |
| **Criterios de aceptación** | • El SP `sp_marcar_trials_vencidos()` recorre los prospectos con `fecha_fin_prueba < CURDATE()` que no estén en `Convertido` ni `Inadecuado`.<br>• Devuelve la cantidad de filas afectadas (`ROW_COUNT()`) y la fecha del proceso.<br>• Encadena los triggers BEFORE UPDATE (resetea score a 0) y AFTER UPDATE (escribe auditoría en `REPORTE`).<br>• Está expuesto en `POST /api/automatizacion/limpiar-trials-vencidos`. |
| **Responsable** | Julian Mateo Artunduaga Gomez |

### 3.3 Módulo 12 — Funciones UDF
**Responsable del módulo:** Valery Tatiana Pamplona Gómez

| HU-35 | Historia de Usuario |
|---|---|
| **Descripción** | Como equipo de desarrollo, quiero centralizar en la base de datos la lógica de etiquetar el scoring numérico como `Alto`/`Medio`/`Bajo`, evitando que viva duplicada entre el front-end y otros consumidores. |
| **Criterios de aceptación** | • La UDF `fn_nivel_interes(p_puntuacion)` retorna `'Alto'` si la puntuación es ≥ 15, `'Medio'` si es ≥ 5 y `'Bajo'` en otro caso.<br>• Está declarada como `DETERMINISTIC` para permitir su uso en índices o vistas materializadas.<br>• Se expone en `GET /api/automatizacion/funciones/nivel-interes?puntuacion=N` y se puede consultar desde la sección "Funciones UDF" de la página de Automatización. |
| **Responsable** | Valery Tatiana Pamplona Gómez |

| HU-36 | Historia de Usuario |
|---|---|
| **Descripción** | Como vendedor, quiero saber cuántos días faltan para que termine el trial de un prospecto, calculado por la base de datos. |
| **Criterios de aceptación** | • La UDF `fn_dias_restantes_trial(p_id_prospecto)` devuelve `DATEDIFF(fecha_fin_prueba, CURDATE())`.<br>• Retorna `NULL` si el prospecto no tiene `fecha_fin_prueba` configurada.<br>• Devuelve valor negativo si el trial ya venció (caso útil para reportes de morosidad).<br>• Está expuesta en `GET /api/automatizacion/funciones/dias-restantes/{id_prospecto}`. |
| **Responsable** | Hayder Esteban Barrera Pérez |

| HU-37 | Historia de Usuario |
|---|---|
| **Descripción** | Como gerente comercial, quiero conocer el lifetime value (LTV) de un cliente, calculado como la suma de sus ventas pagadas. |
| **Criterios de aceptación** | • La UDF `fn_lifetime_value(p_id_cliente)` devuelve `SUM(monto)` filtrando por `estado = 'Pagada'`.<br>• Retorna 0 si el cliente no tiene ventas pagadas (`COALESCE`).<br>• Está expuesta en `GET /api/automatizacion/funciones/lifetime-value/{id_cliente}` y disponible en la sección de Automatización. |
| **Responsable** | Valery Tatiana Pamplona Gómez |

### 3.4 Módulo 13 — Front-end conectado
**Responsable del módulo:** Equipo completo

| HU-38 | Historia de Usuario |
|---|---|
| **Descripción** | Como evaluador, quiero una página dedicada que demuestre cada objeto avanzado de la base (trigger, SP, UDF) consumido desde botones reales del front-end. |
| **Criterios de aceptación** | • La página `automatizacion.html` agrupa los SPs y UDFs en tarjetas con sus respectivos botones de invocación.<br>• Cada acción muestra el resultado del backend (tag `COMMIT` verde / `ROLLBACK` rojo) y los datos retornados.<br>• La sección final muestra la bitácora de cambios de estado leída de `REPORTE` y poblada por el trigger.<br>• Está enlazada en el nav junto a Inicio, Prospectos, Ventas, Datos y Automatización. |
| **Responsable** | Equipo completo |

| HU-39 | Historia de Usuario |
|---|---|
| **Descripción** | Como evaluador, quiero un explorador genérico para ver el contenido completo de las 9 tablas del sistema, sin tener que abrir Swagger o un cliente SQL. |
| **Criterios de aceptación** | • La página `datos.html` tiene 9 chips (uno por tabla) que cargan el endpoint REST correspondiente al click.<br>• Cada tabla se renderiza con columnas con formato apropiado: dinero en COP, fechas localizadas, booleanos como badges Sí/No, JSON parseado para la columna `resultado` de `REPORTE`.<br>• Un buscador genérico filtra por cualquier columna visible.<br>• El contador muestra "X de Y registros". |
| **Responsable** | Equipo completo |

| HU-40 | Historia de Usuario |
|---|---|
| **Descripción** | Como comercial, quiero extender el trial directamente desde la tarjeta del prospecto en la página de Prospectos. |
| **Criterios de aceptación** | • Los prospectos con `fecha_fin_prueba` y estado distinto a `Convertido` / `Inadecuado` muestran un botón "⏰ Extender trial".<br>• Al hacer click, se solicita el número de días (1-90) y se invoca el SP a través del endpoint del backend.<br>• El resultado muestra fecha anterior, fecha nueva y días sumados, refrescando la vista. |
| **Responsable** | Equipo completo |

---

## 4. Script SQL (sección Sesión 3 de `zimbra_crm.sql`)

### 4.1 Decisión de diseño: usar las 9 tablas originales

La decisión más importante de esta entrega fue **no crear ninguna tabla nueva**. El modelo relacional de la Sesión 1 ya incluye 9 tablas con responsabilidades bien diferenciadas; agregar tablas auxiliares para la auditoría habría roto la coherencia del modelo y duplicado información que la tabla `REPORTE` ya puede albergar.

En consecuencia, la bitácora del trigger de auditoría se materializa como filas de `REPORTE` con `tipo_reporte = 'Auditoria Estado Prospecto'` y un payload JSON en el campo `resultado`. La operación es 100% compatible con el esquema original.

### 4.2 Triggers implementados

| # | Trigger | Evento | Regla de negocio |
|---|---|---|---|
| 1 | `trg_interaccion_actualiza_scoring` | AFTER INSERT en `INTERACCION_MARKETING` | Suma `peso_scoring` y promueve a `Calificado` si supera 15 estando en estado promovible. |
| 2 | `trg_propuesta_aceptada_promueve_prospecto` | AFTER UPDATE en `PROPUESTA` | Al pasar a `Aceptada`, marca al prospecto como `Convertido`. |
| 3 | `trg_prospecto_inadecuado_resetea_score` | BEFORE UPDATE en `PROSPECTO` | Si el nuevo estado es `Inadecuado`, fuerza `puntuacion = 0`. |
| 4 | `trg_audit_estado_prospecto` | AFTER UPDATE en `PROSPECTO` | Inserta en `REPORTE` un evento de auditoría con JSON. |

### 4.3 Procedimientos almacenados

| # | Procedimiento | Caso de negocio |
|---|---|---|
| 1 | `sp_reporte_mensual_ventas(p_anio, p_mes)` | Cierre comercial mensual. Calcula totales y top campaña, persiste el reporte. |
| 2 | `sp_extender_trial(p_id_prospecto, p_dias)` | Extender el trial de un prospecto entre 1 y 90 días, con validaciones. |
| 3 | `sp_marcar_trials_vencidos()` | Limpieza periódica que marca como `Inadecuado` los prospectos con trial vencido. |

### 4.4 Funciones UDF

| # | Función | Retorno | Caso de negocio |
|---|---|---|---|
| 1 | `fn_nivel_interes(p_puntuacion)` | `VARCHAR(10)` | Etiqueta cualitativa del scoring: `Alto`/`Medio`/`Bajo`. |
| 2 | `fn_dias_restantes_trial(p_id_prospecto)` | `INT` | Días restantes del trial (negativo si venció, `NULL` si no aplica). |
| 3 | `fn_lifetime_value(p_id_cliente)` | `DECIMAL(14,2)` | Suma de ventas pagadas del cliente. |

### 4.5 Refresco de fechas de prueba

Las fechas estáticas insertadas en la Sesión 2 ya pasaron respecto a la fecha de sustentación. El script incluye 5 `UPDATE` que mueven `fecha_fin_prueba` de prospectos seleccionados a `CURDATE() + 1..7 días`, lo que garantiza que la métrica **"Trials por vencer"** del dashboard muestre valores > 0 al abrir la app. Estos `UPDATE` no cambian el estado del prospecto, por lo cual el trigger de auditoría no se dispara.

---

## 5. Back-end con endpoints funcionales

### 5.1 Nuevo router `automatizacion`

`app/routers/automatizacion.py` expone los siguientes endpoints (prefijo `/api/automatizacion`):

| Método | Endpoint | Objeto SQL invocado |
|---|---|---|
| POST | `/reporte-mensual` | `CALL sp_reporte_mensual_ventas(anio, mes)` |
| POST | `/extender-trial/{id_prospecto}?dias=N` | `CALL sp_extender_trial(id, dias)` |
| POST | `/limpiar-trials-vencidos` | `CALL sp_marcar_trials_vencidos()` |
| GET | `/funciones/nivel-interes?puntuacion=N` | `SELECT fn_nivel_interes(N)` |
| GET | `/funciones/dias-restantes/{id_prospecto}` | `SELECT fn_dias_restantes_trial(id)` |
| GET | `/funciones/lifetime-value/{id_cliente}` | `SELECT fn_lifetime_value(id)` |
| GET | `/auditoria` | `SELECT` sobre `REPORTE` filtrando `tipo_reporte='Auditoria Estado Prospecto'` + parsing del JSON |

Los endpoints validan parámetros vía Pydantic, atrapan los `SIGNAL SQLSTATE '45000'` lanzados por los SPs y los devuelven como respuestas `400 Bad Request` con el mensaje original del SP, conservando la trazabilidad de la regla violada.

### 5.2 Ajuste del servicio de scoring (delegación en trigger)

El servicio `app/services/scoring_service.py` fue **simplificado** para delegar el cálculo del scoring en el trigger MySQL. La versión anterior hacía:

1. `INSERT INTO INTERACCION_MARKETING`
2. `UPDATE PROSPECTO SET puntuacion = puntuacion + N`
3. `UPDATE PROSPECTO SET estado = 'Calificado'` si cruza el umbral

La nueva versión hace solo el paso 1 dentro de `with db.begin():`; los pasos 2 y 3 los ejecuta el trigger `trg_interaccion_actualiza_scoring` automáticamente. Después del `db.flush()` se hace `db.refresh(prospecto)` para devolver al cliente los valores actualizados por el trigger. La transacción atómica se preserva — el trigger corre dentro del mismo `BEGIN`.

### 5.3 Validación vía Swagger

Todos los nuevos endpoints quedan documentados automáticamente en `http://localhost:8000/docs` bajo el tag **"Automatización (Triggers/SP/UDF)"**, lo que permite al evaluador ejecutarlos sin pasar por el front-end.

---

## 6. Front-end CONECTADO

El requisito de la Sesión 3 enfatiza que el front-end debe estar CONECTADO. La presente entrega aporta tres componentes web nuevos, todos contra los endpoints REST del backend.

### 6.1 Página `automatizacion.html`

Página dedicada a demostrar los objetos avanzados de la BD. Está dividida en tres secciones:

- **📦 Procedimientos almacenados** — tarjetas con formularios y botones que invocan los 3 SPs. Cada resultado muestra los datos retornados por la BD y un tag `COMMIT` o `ROLLBACK` según el desenlace.
- **🧮 Funciones UDF** — tarjetas con inputs para invocar las 3 UDFs y ver el resultado serializado.
- **📜 Bitácora de cambios de estado** — tabla que consume `GET /api/automatizacion/auditoria` y muestra los cambios poblados por el trigger.

### 6.2 Página `datos.html` — Explorador de las 9 tablas

Página adicional creada para resolver una preocupación de usabilidad: el evaluador necesita ver el contenido de las 9 tablas sin abrir Swagger ni un cliente SQL. La página presenta 9 chips (uno por tabla); al hacer click se consulta el endpoint REST correspondiente y se renderiza una tabla HTML con formato apropiado por columna. Incluye buscador genérico, contador de filas y soporte para JSON pretty-print en la columna `resultado` de `REPORTE` (para que la bitácora del trigger sea legible).

### 6.3 Botón "Extender trial" en la página de Prospectos

La tarjeta de cada prospecto con trial activo y estado promovible muestra un botón **⏰ Extender trial**. Al hacer click, el usuario indica los días a sumar y la UI invoca el endpoint que llama al SP `sp_extender_trial`. El resultado muestra la fecha anterior, la nueva y los días sumados.

### 6.4 Actualización del flujo de scoring

El modal de "Registrar interacción" en la página de Prospectos sigue siendo idéntico desde la perspectiva del usuario, pero ahora el flujo aprovecha el trigger: el backend solo hace `INSERT`, el trigger calcula y promueve, el backend vuelve a leer al prospecto y devuelve el resultado actualizado. El usuario sigue viendo "🎉 Prospecto promovido a Calificado" cuando corresponda, pero la lógica ya no vive en Python.

---

## 7. Manual de ejecución

Los pasos son idénticos a la Sesión 2; el único cambio es que el script `zimbra_crm.sql` ahora incluye también la parte de Sesión 3, por lo cual basta con cargarlo una sola vez para tener triggers, SPs y UDFs creados.

### Paso 1 — Cargar el script SQL completo

```bash
mysql -u root -p < sql/zimbra_crm.sql
```

El script crea la base de datos, las 9 tablas, los 30+ registros por tabla, ejecuta las 7 transacciones de la Sesión 2 y al final crea los 4 triggers, 3 SPs y 3 UDFs de la Sesión 3.

Verificar el resultado:

```bash
mysql -u root -p zimbra_crm -e "SHOW TRIGGERS;"
mysql -u root -p zimbra_crm -e "SHOW PROCEDURE STATUS WHERE Db = 'zimbra_crm';"
mysql -u root -p zimbra_crm -e "SHOW FUNCTION STATUS  WHERE Db = 'zimbra_crm';"
```

### Paso 2 — Levantar el backend

Con Docker:

```bash
docker compose down -v
docker compose up --build
```

Sin Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # editar credenciales
uvicorn app.main:app --reload
```

### Paso 3 — Validar Sesión 3 en el navegador

| URL | Validación |
|---|---|
| `http://localhost:8000/` | Dashboard con métricas reales; "Trials por vencer" muestra ≥ 5 (gracias al refresco de fechas). |
| `http://localhost:8000/prospectos.html` | Botón "⏰ Extender trial" disponible en tarjetas con trial activo. |
| `http://localhost:8000/automatizacion.html` | Botones para los 3 SPs, inputs para las 3 UDFs, bitácora del trigger de auditoría. |
| `http://localhost:8000/datos.html` | Chips para explorar las 9 tablas. |
| `http://localhost:8000/docs` | Tag **"Automatización (Triggers/SP/UDF)"** con los 7 endpoints documentados. |

---

## 8. Cierre

La presente entrega cumple integralmente con los entregables solicitados para la Sesión 3:

- **Script SQL con triggers, procedimientos y funciones** — 4 triggers + 3 SPs + 3 UDFs integrados al final del archivo único `sql/zimbra_crm.sql`, respetando la decisión de diseño de no crear tablas adicionales.
- **Código del back-end con endpoints funcionales** — router `automatizacion` con 7 endpoints documentados en Swagger; servicio de scoring rediseñado para delegar en el trigger.
- **Front-end CONECTADO** — página de automatización con botones reales, explorador de las 9 tablas y botón "Extender trial" integrado en la página de prospectos.

El trabajo realizado completa el ciclo del proyecto: del diseño y los requerimientos de la Sesión 1, a la implementación SQL con transacciones ACID de la Sesión 2, a la automatización en la propia base de datos de la Sesión 3. El sistema queda listo para sustentación con un caso de negocio coherente, datos reales en las 9 tablas y lógica avanzada que se demuestra desde la interfaz web.

---

**Firma del equipo:**
Hayder Esteban Barrera Pérez · Julian Mateo Artunduaga Gomez · Valery Tatiana Pamplona Gómez
UNIMINUTO — Ingeniería de Sistemas — 2026