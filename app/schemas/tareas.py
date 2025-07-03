from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class Tarea(BaseModel):
    id_causa: str = Field(..., pattern=r'^C-\d{4}-\d{3}$')  # Ej: C-2024-001
    id_tarea: None|str = Field(None, pattern=r'^C-\d{4}-\d{3}-T\d{3}$')  # Ej: C-2024-001-T001
    nombre:str
    descripcion:str=""
    respuestas:str=""
    fecha_creacion:None|datetime=None
    fecha_ultima_actualizacion:None|datetime=None
    estado:Literal["pendiente", "en_proceso", "completada"]