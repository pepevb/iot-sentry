"""
IoT Sentry - Configuración de Base de Datos
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .models import Base

# Directorio de datos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Ruta de la base de datos SQLite
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'iotsentry.db')}"

# Crear engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necesario para SQLite
    echo=False  # Cambiar a True para debug SQL
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializar la base de datos creando todas las tablas
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de datos inicializada en: {DATABASE_URL}")


@contextmanager
def get_db():
    """
    Context manager para obtener sesión de base de datos

    Uso:
        with get_db() as db:
            devices = db.query(Device).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Obtener sesión de base de datos (para FastAPI dependency injection)

    Uso en FastAPI:
        @app.get("/devices")
        def get_devices(db: Session = Depends(get_db_session)):
            return db.query(Device).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Inicializar base de datos al importar
init_db()
