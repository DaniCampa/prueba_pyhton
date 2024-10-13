from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

# Configuración de SQLite
DATABASE_URL = "sqlite:///./candidato.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Modelo de base de datos para SQLite
class Candidato(Base):
    __tablename__ = "candidatos"

    id: int = Column(Integer, primary_key=True, index=True)
    dni: str = Column(String, unique=True, index=True)
    nombre: str = Column(String)
    apellido: str = Column(String)


# Crear las tablas
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()


# Modelo de datos para el endpoint POST
class CandidatoCreate(BaseModel):
    dni: str
    nombre: str
    apellido: str


# Endpoint POST para recibir datos y almacenarlos en SQLite
@app.post("/candidato")
def create_candidato(candidato: CandidatoCreate) -> dict:
    """
    Crea un nuevo candidato en la base de datos SQLite.

    Args:
        candidato (CandidatoCreate): Datos del candidato a crear.

    Returns:
        dict: Mensaje de éxito y datos del candidato creado.

    Raises:
        HTTPException: Si el candidato con el mismo DNI ya existe.
    """
    db: Session = SessionLocal()

    # Verificar si el DNI ya existe
    existing_candidato = db.query(Candidato).filter(Candidato.dni == candidato.dni).first()
    if existing_candidato:
        raise HTTPException(status_code=400, detail="Candidato con este DNI ya existe.")

    # Crear un nuevo registro
    nuevo_candidato = Candidato(dni=candidato.dni, nombre=candidato.nombre, apellido=candidato.apellido)
    db.add(nuevo_candidato)
    db.commit()
    db.refresh(nuevo_candidato)

    return {"mensaje": "Candidato creado con éxito", "candidato": nuevo_candidato}
