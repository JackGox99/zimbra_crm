"""
Schemas Pydantic para CLIENTE.

Cliente es 1:1 con un PROSPECTO (UNIQUE en id_prospecto). El campo
sync_salesforce simula la integración con Salesforce.com mediante un
flag booleano y fecha_ult_sync con la marca temporal del último éxito.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteBase(BaseModel):
    """Campos comunes de un cliente."""

    nombre: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr
    empresa: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    fecha_registro: date
    id_prospecto: int | None = None
    sync_salesforce: bool
    fecha_ult_sync: datetime | None = None


class ClienteCreate(ClienteBase):
    """Payload para POST /api/clientes."""


class ClienteUpdate(BaseModel):
    """Payload para PUT /api/clientes/{id}."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    correo: EmailStr | None = None
    empresa: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    fecha_registro: date | None = None
    id_prospecto: int | None = None
    sync_salesforce: bool | None = None
    fecha_ult_sync: datetime | None = None


class ClienteOut(ClienteBase):
    """Respuesta serializada desde el ORM."""

    id_cliente: int

    model_config = ConfigDict(from_attributes=True)
