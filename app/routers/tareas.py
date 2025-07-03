from fastapi import (
    APIRouter, 
    Depends,
    HTTPException,
    status)
from fastapi.encoders import jsonable_encoder
from ..core.security import validate_api_key
from ..schemas.tareas import Tarea
from ..db import collection_tareas
import re
from datetime import datetime, UTC

router = APIRouter(
    tags=["Tareas"],
    dependencies=[Depends(validate_api_key)],
    responses={404: {"description": "Not found"}},
    prefix="/tareas"
)

@router.post("/")
async def crear_tarea(request: Tarea):
    # 1. Comprobar si ya existe una causa con ese id_causa
    existente = await collection_tareas.find_one(
        {"id_tarea": request.id_tarea},
        projection={"_id":0}
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una tarea con ese id_tarea."
        )

    # 2. Si no existe, crearla
    now = datetime.now(UTC)
    request.fecha_creacion = now
    request.fecha_ultima_actualizacion = now

    id_tarea = await obtener_proximo_id(request.id_causa)
    request.id_tarea = id_tarea['proximo_id']

    document = jsonable_encoder(request)
    await collection_tareas.insert_one(document)
    
    if "_id" in document:
        del document["_id"]
    
    return document

@router.get("/{id_tarea}/")
async def obtener_tarea(id_tarea:str):
    document = await collection_tareas.find_one(
        {"id_tarea":id_tarea},
        projection={"_id":0}
    )
    if document:
        return document
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró la tarea"
    )

@router.get("/causa/{id_causa}/")
async def obtener_todas_tareas(id_causa:str):
    documents = await collection_tareas.find(
        {"id_causa":id_causa},
        projection={"_id":0}
    ).to_list(100)
    if documents:
        return documents
    
    return []

@router.put("/{id_tarea}/")
async def actualizar_tarea(id_tarea:str, request:Tarea):
    tarea_db = await collection_tareas.find_one(
        {"id_tarea":id_tarea},
        projection={"_id":0}
    )
    if not tarea_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la tarea a actualizar"
        )
    now = datetime.now(UTC)
    request.fecha_ultima_actualizacion = now
    document = jsonable_encoder(request)
    await collection_tareas.update_one(
        {"id_tarea":id_tarea},
        {"$set":document}
    )
    return document

@router.patch("/{id_tarea}/")
async def actualizar_tarea_parte(id_tarea:str, request:Tarea):
    tarea_db = await collection_tareas.find_one(
        {"id_tarea":id_tarea},
        projection={"_id":0}
    )
    if not tarea_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la tarea a actualizar"
        )
    
    tarea_model = Tarea(**tarea_db)

    update_data = request.model_dump(exclude_unset=True)

    tarea_model_update = tarea_model.model_copy(update=update_data)
    
    tarea_model_update.fecha_ultima_actualizacion = datetime.now(UTC)
    
    document = jsonable_encoder(tarea_model_update)

    await collection_tareas.update_one(
        {"id_tarea":id_tarea},
        {"$set":document}
    )
    return document

@router.delete("/{id_tarea}/")
async def eliminar_tarea(id_tarea:str):
    await collection_tareas.delete_one({"id_tarea":id_tarea})
    return {"message": "Tarea eliminada exitosamente"}

@router.get("/proximo/id/{id_causa}/")
async def obtener_proximo_id(id_causa:str):
    
    regex_pattern = f"^{id_causa}-T\\d{{3}}$"
    ultimo = await collection_tareas.find_one(
        {"id_tarea": {"$regex": regex_pattern}},
        projection={"_id":0},
        sort=[("id_tarea", -1)]
    )
    if ultimo and "id_tarea" in ultimo:
        match = re.match(rf"{id_causa}-T(\d{{3}})", ultimo["id_tarea"])
        if match:
            correlativo = int(match.group(1)) + 1
        else:
            correlativo = 1
    else:
        correlativo = 1
    
    proximo_id = f"{id_causa}-T{str(correlativo).zfill(3)}"
    
    return {"proximo_id": proximo_id}
