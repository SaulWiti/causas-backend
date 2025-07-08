from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

# Submodelos para las partes (demandante/demandado)
class Parte(BaseModel):
    nombre: str
    rut: None|str
    abogado: None|str
    contacto: None|str = None

class Tribunal(BaseModel):
    nombre: str
    rol_tribunal: str = Field(..., alias="rol_tribunal")

# Modelo Base
class Causa(BaseModel):
    id_causa: str = Field(..., pattern=r'^C-\d{4}-\d{3}$')  # Ej: C-2024-001
    titulo: str = Field(..., min_length=5, max_length=200)
    descripcion: str
    estado: Literal["ingresada", "en_tramite", "resuelta", "archivada"]
    fecha_creacion: None|datetime = None
    fecha_ultima_actualizacion: None|datetime = None
    tipo: Literal["civil", "penal", "laboral", "familia"]
    partes: dict[Literal["demandante", "demandado"], Parte]
    tribunal: Tribunal
    notas: None|str = None
    usuario_responsable: None|EmailStr = None

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id_causa": "C-2025-001",
                "titulo": "Demanda por incumplimiento de contrato",
                "descripcion": "El demandante alega falta de pago según contrato firmado el 15/03/2024",
                "estado": "en_tramite",
                "fecha_creacion": "2025-06-16T10:00:00Z",
                "fecha_ultima_actualizacion": "2025-06-16T15:30:00Z",
                "tipo": "civil",
                "partes": {
                    "demandante": {
                        "nombre": "Juan Pérez",
                        "rut": "12.345.678-9",
                        "abogado": "María González",
                        "contacto": "+56912345678"
                    },
                    "demandado": {
                        "nombre": "Empresa XYZ S.A.",
                        "rut": "76.543.210-K",
                        "abogado": "Pedro Sánchez"
                    }
                },
                "tribunal": {
                    "nombre": "Juzgado Civil de Santiago",
                    "rol_tribunal": "C-1245-2025"
                },
                "notas": "El demandado solicitó ampliación de plazo",
                "usuario_responsable": "abogado1@estudio.cl"
            }
        }

class CausaDB(Causa):
    id: None|ObjectId = Field(alias="_id", default=None)

    class Config:
        arbitrary_types_allowed = True  # Para permitir ObjectId
        json_encoders = {
            ObjectId: str  # Convierte ObjectId a string en JSON
        }