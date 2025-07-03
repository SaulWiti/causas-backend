from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId

class Tarea(BaseModel):
    id_causa: str = Field(..., pattern=r'^C-\d{4}-\d{3}$')  # Ej: C-2024-001
    id_tarea: str = Field(..., pattern=r'^C-\d{4}-\d{3}-T\d{3}$')  # Ej: C-2024-001-T001
    nombre:str
    descripcion:str
    respuestas:str
    fecha_creacion:datetime
    fecha_ultima_actualizacion:datetime
    estado:Literal["pendiente", "en_proceso", "completada"]