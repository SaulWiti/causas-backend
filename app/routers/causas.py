from fastapi import (
    APIRouter, 
    Depends,
    HTTPException,
    status)
from fastapi.encoders import jsonable_encoder
from ..core.security import validate_api_key
from ..models.causas import Causa
from ..db import collection_causas
import re
from datetime import datetime, UTC

router = APIRouter(
    tags=["Causas"],
    dependencies=[Depends(validate_api_key)],
    responses={404: {"description": "Not found"}},
    prefix="/causas"
)


@router.post("/")
async def crear_causa(request: Causa):
    # 1. Comprobar si ya existe una causa con ese id_causa
    existente = await collection_causas.find_one(
        {"id_causa": request.id_causa},
        projection={"_id":0}
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una causa con ese id_causa."
        )
    
    # 2. Si no existe, crearla
    now = datetime.now(UTC)
    request.fecha_creacion = now
    request.fecha_ultima_actualizacion = now

    document = jsonable_encoder(request)
    await collection_causas.insert_one(document)
    
    if "_id" in document:
        del document["_id"]
    
    return document


@router.get("/{id_causa}/")
async def obtener_causa(id_causa:str):
    document = await collection_causas.find_one(
        {"id_causa":id_causa},
        projection={"_id":0}
    )
    if document:
        return document
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró la causa"
    )


@router.get("/")
async def obtener_todas_causas():
    documents = await collection_causas.find(
        projection={"_id":0}
    ).to_list(100)
    if documents:
        return documents
    
    return []


@router.put("/{id_causa}/")
async def actualizar_causa(id_causa:str, request:Causa):
    causa_db = await collection_causas.find_one(
        {"id_causa":id_causa},
        projection={"_id":0}
    )
    if not causa_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la causa a actualizar"
        )
    now = datetime.now(UTC)
    request.fecha_ultima_actualizacion = now
    document = jsonable_encoder(request)
    await collection_causas.update_one(
        {"id_causa":id_causa},
        {"$set":document}
    )
    return document


@router.patch("/{id_causa}/")
async def actualizar_causa_parte(id_causa:str, request:Causa):
    causa_db = await collection_causas.find_one(
        {"id_causa":id_causa},
        projection={"_id":0}
    )
    if not causa_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la causa a actualizar"
        )
    
    causa_model = Causa(**causa_db)

    update_data = request.model_dump(exclude_unset=True)

    causa_model_update = causa_model.model_copy(update=update_data)
    
    causa_model_update.fecha_ultima_actualizacion = datetime.now(UTC)
    
    document = jsonable_encoder(causa_model_update)

    await collection_causas.update_one(
        {"id_causa":id_causa},
        {"$set":document}
    )
    return document

@router.delete("/{id_causa}/")
async def eliminar_causa(id_causa:str):
    await collection_causas.delete_one({"id_causa":id_causa})
    return {"message": "Causa eliminada exitosamente"}


@router.get("/proximo/id/")
async def obtener_proximo_id():
    anio = datetime.now().year
    
    regex_pattern = f"^C-{anio}-\\d{{3}}$"
    ultimo = await collection_causas.find_one(
        {"id_causa": {"$regex": regex_pattern}},
        projection={"_id":0},
        sort=[("id_causa", -1)]
    )
    print("ultimo encontrado:", ultimo)
    if ultimo and "id_causa" in ultimo:
        match = re.match(rf"C-{anio}-(\d{{3}})", ultimo["id_causa"])
        if match:
            correlativo = int(match.group(1)) + 1
        else:
            correlativo = 1
    else:
        correlativo = 1
    

    proximo_id = f"C-{anio}-{str(correlativo).zfill(3)}"
    
    return {"proximo_id": proximo_id}

