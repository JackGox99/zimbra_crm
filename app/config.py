"""
Configuración de la aplicación.

Carga las variables de entorno desde el archivo `.env` ubicado en la raíz
del proyecto y las expone tipadas mediante la clase `Settings`. Nunca se
deben hardcodear credenciales: todo dato sensible debe pasar por aquí.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto: dos niveles arriba de este archivo (app/config.py -> raíz).
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# Carga las variables del archivo .env si existe.
load_dotenv(PROJECT_ROOT / ".env")


def _read_env(name: str, default: str | None = None) -> str:
    """Lee una variable de entorno; lanza error si no existe y no hay default."""
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(
            f"Variable de entorno '{name}' no definida. "
            f"Copia .env.example a .env y configura los valores."
        )
    return value


@dataclass(frozen=True)
class Settings:
    """Contenedor inmutable con la configuración del sistema."""

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    api_host: str
    api_port: int

    @property
    def database_url(self) -> str:
        """URL de conexión SQLAlchemy para MySQL vía PyMySQL."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )


# Instancia única utilizada por el resto de la aplicación.
settings = Settings(
    db_host=_read_env("DB_HOST", "127.0.0.1"),
    db_port=int(_read_env("DB_PORT", "3306")),
    db_user=_read_env("DB_USER", "root"),
    db_password=_read_env("DB_PASSWORD", ""),
    db_name=_read_env("DB_NAME", "zimbra_crm"),
    api_host=_read_env("API_HOST", "127.0.0.1"),
    api_port=int(_read_env("API_PORT", "8000")),
)
