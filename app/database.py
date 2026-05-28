"""
Capa de acceso a datos.

Define el engine de SQLAlchemy, la fábrica de sesiones y la clase Base de
la cual heredan todos los modelos. También expone la dependencia
`get_db()` que FastAPI inyecta en los endpoints para entregar una Session
viva por petición y cerrarla al terminar.

Decisiones clave para soportar transacciones ACID:
  * autocommit=False  → cada operación queda dentro de una transacción
                        explícita que debe ser confirmada con commit()
                        o revertida con rollback().
  * autoflush=False   → evita flushes implícitos que disparen SQL antes
                        de tiempo y oculten el control transaccional.
  * expire_on_commit=False → permite seguir accediendo a los objetos
                        tras el commit sin disparar SELECTs adicionales,
                        útil al devolver entidades en las respuestas.
"""

from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# Engine: pool con pre-ping para detectar conexiones muertas y reciclado
# horario para evitar problemas con timeouts del servidor MySQL.
engine = create_engine(
    settings.database_url,
    echo=True,            # Imprime cada sentencia SQL (BEGIN, SAVEPOINT, COMMIT,
                          # ROLLBACK, etc.) en los logs del contenedor. Útil para
                          # sustentar las transacciones ACID en vivo.
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

# Fábrica de sesiones. Las sesiones se crean por petición HTTP.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM del proyecto."""


def get_db() -> Iterator[Session]:
    """
    Dependencia de FastAPI que produce una Session por petición.

    La Session se cierra siempre al terminar la petición, incluso si la
    vista lanzó una excepción. No hace commit/rollback automático: la
    capa de servicio es la responsable explícita de la transacción para
    que las propiedades ACID queden visibles en el código.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
