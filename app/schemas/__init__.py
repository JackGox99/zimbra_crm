"""
Schemas Pydantic v2 para validación de entrada/salida de la API.

Cada entidad expone tres schemas estándar:
  * XxxCreate  → payload de POST (todos los campos requeridos)
  * XxxUpdate  → payload de PUT  (todos los campos opcionales)
  * XxxOut     → respuesta serializada desde el ORM (incluye id)

Más algunos schemas auxiliares para endpoints transaccionales
(p.ej. CerrarVentaIn / CerrarVentaOut en venta.py).
"""

from app.schemas.campana import (
    CampanaCreate,
    CampanaOut,
    CampanaUpdate,
)
from app.schemas.cliente import (
    ClienteCreate,
    ClienteOut,
    ClienteUpdate,
)
from app.schemas.comunicacion_enviada import (
    ComunicacionEnviadaCreate,
    ComunicacionEnviadaOut,
    ComunicacionEnviadaUpdate,
)
from app.schemas.interaccion_marketing import (
    InteraccionMarketingCreate,
    InteraccionMarketingOut,
    InteraccionMarketingUpdate,
    RegistrarInteraccionOut,
)
from app.schemas.plantilla_comunicacion import (
    PlantillaComunicacionCreate,
    PlantillaComunicacionOut,
    PlantillaComunicacionUpdate,
)
from app.schemas.propuesta import (
    PropuestaCreate,
    PropuestaOut,
    PropuestaUpdate,
)
from app.schemas.prospecto import (
    ProspectoCreate,
    ProspectoOut,
    ProspectoUpdate,
)
from app.schemas.reporte import (
    EmbudoConversionOut,
    RendimientoCampanaOut,
    ReporteCreate,
    ReporteOut,
    ReporteUpdate,
)
from app.schemas.venta import (
    CerrarVentaIn,
    CerrarVentaOut,
    VentaCreate,
    VentaOut,
    VentaUpdate,
)

__all__ = [
    "CampanaCreate", "CampanaUpdate", "CampanaOut",
    "ClienteCreate", "ClienteUpdate", "ClienteOut",
    "ComunicacionEnviadaCreate", "ComunicacionEnviadaUpdate", "ComunicacionEnviadaOut",
    "InteraccionMarketingCreate", "InteraccionMarketingUpdate", "InteraccionMarketingOut",
    "RegistrarInteraccionOut",
    "PlantillaComunicacionCreate", "PlantillaComunicacionUpdate", "PlantillaComunicacionOut",
    "PropuestaCreate", "PropuestaUpdate", "PropuestaOut",
    "ProspectoCreate", "ProspectoUpdate", "ProspectoOut",
    "ReporteCreate", "ReporteUpdate", "ReporteOut",
    "EmbudoConversionOut", "RendimientoCampanaOut",
    "VentaCreate", "VentaUpdate", "VentaOut",
    "CerrarVentaIn", "CerrarVentaOut",
]
