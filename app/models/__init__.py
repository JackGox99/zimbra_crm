"""
Modelos SQLAlchemy del dominio Zimbra CRM.

Importar este paquete (o cualquiera de sus modelos) registra todas las
clases en el `metadata` de Base, lo cual es indispensable para que
SQLAlchemy resuelva correctamente las relaciones cruzadas declaradas
con strings (back_populates apuntando a clases definidas en otros
archivos).
"""

from app.models.campana import Campana
from app.models.cliente import Cliente
from app.models.comunicacion_enviada import ComunicacionEnviada
from app.models.interaccion_marketing import InteraccionMarketing
from app.models.plantilla_comunicacion import PlantillaComunicacion
from app.models.propuesta import Propuesta
from app.models.prospecto import Prospecto
from app.models.reporte import Reporte
from app.models.venta import Venta

__all__ = [
    "Campana",
    "Cliente",
    "ComunicacionEnviada",
    "InteraccionMarketing",
    "PlantillaComunicacion",
    "Propuesta",
    "Prospecto",
    "Reporte",
    "Venta",
]
