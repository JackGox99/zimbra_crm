"""
Punto de entrada de la aplicación FastAPI.

Configura:
  * Metadatos para Swagger UI (título, descripción, versión).
  * CORS abierto para que el frontend y herramientas como Postman puedan
    consumir la API durante la sustentación.
  * Endpoint de healthcheck `/api/health`.
  * Servido de archivos estáticos del frontend (HTML/CSS/JS vanilla) en
    la raíz `/`, con `html=True` para que `index.html` actúe como página
    por defecto y los demás `.html` queden accesibles por su ruta.

Los routers de cada entidad se irán incluyendo aquí a medida que se
construyan en los pasos siguientes del proyecto.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"


app = FastAPI(
    title="Zimbra CRM — Sistema Transaccional",
    description=(
        "API REST del CRM de Zimbra Collaboration Suite (ZCS). "
        "Cubre la gestión de campañas, prospectos, propuestas, clientes y "
        "ventas con transacciones explícitas sobre MySQL 8."
        "\n\n"
        "**Equipo:** Hayder Esteban Barrera Pérez · Julian Mateo Artunduaga "
        "Gomez · Valery Tatiana Pamplona Gómez  \n"
        "**Docente:** Ladi Paola Ballen Carrasco  \n"
        "**Asignatura:** Sistemas Transaccionales de Bases de Datos — UNIMINUTO"
    ),
    version="1.0.0",
)

# --- CORS ----------------------------------------------------------------
# Permisivo a propósito: el frontend se sirve desde el mismo origen, pero
# durante la sustentación también queremos poder probar con Postman, curl
# o el navegador en otro puerto sin restricciones.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints utilitarios ----------------------------------------------
@app.get("/api/health", tags=["health"], summary="Healthcheck de la API")
def health() -> dict[str, str]:
    """Verifica que la API esté arriba. No toca la base de datos."""
    return {"status": "ok", "api": "zimbra_crm", "version": app.version}


# --- Inclusión de routers -----------------------------------------------
from app.routers import (  # noqa: E402  (importación tardía intencional)
    automatizacion,
    campanas,
    clientes,
    comunicaciones,
    interacciones,
    propuestas,
    prospectos,
    reportes,
    ventas,
)

app.include_router(campanas.router, prefix="/api/campanas", tags=["Campañas"])
app.include_router(prospectos.router, prefix="/api/prospectos", tags=["Prospectos"])
app.include_router(interacciones.router, prefix="/api/interacciones", tags=["Interacciones"])
app.include_router(propuestas.router, prefix="/api/propuestas", tags=["Propuestas"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(ventas.router, prefix="/api/ventas", tags=["Ventas"])
app.include_router(
    comunicaciones.router_plantillas,
    prefix="/api/plantillas",
    tags=["Plantillas de comunicación"],
)
app.include_router(
    comunicaciones.router_envios,
    prefix="/api/comunicaciones",
    tags=["Comunicaciones enviadas"],
)
app.include_router(reportes.router, prefix="/api/reportes", tags=["Reportes"])
app.include_router(
    automatizacion.router,
    prefix="/api/automatizacion",
    tags=["Automatización (Triggers/SP/UDF)"],
)


# --- Frontend estático ---------------------------------------------------
# Se monta al final para que los endpoints de la API y los de Swagger
# (/docs, /openapi.json, /redoc) tengan prioridad. `html=True` hace que:
#   * GET /                  -> sirve index.html
#   * GET /prospectos.html   -> sirve frontend/prospectos.html
#   * GET /css/style.css     -> sirve frontend/css/style.css
if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend",
    )


# --- Ejecución directa (opcional) ---------------------------------------
# Permite correr `python -m app.main` además del modo recomendado
# `uvicorn app.main:app --reload`.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
