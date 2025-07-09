from langchain_core.tools import tool
from typing import Literal
from ..bot.bot_state import lock_bot
from ....db import (
    collection_causas, collection_tareas
)
from langgraph.prebuilt import InjectedState
from typing import Annotated
import re

@tool
async def get_causa_by_id(id_causa: str) -> dict | None:
    """
    Busca una causa judicial en la base de datos según su id_causa, validando el formato y corrigiendo la capitalización.

    Parámetros:
    -----------
    id_causa : str
        El identificador único de la causa (ejemplo: "C-2025-001").
        Debe cumplir el formato: C-YYYY-NNN (ejemplo: "C-2025-001").
        Si el usuario ingresa la letra inicial en minúscula, la función la corrige automáticamente.

    Retorna:
    --------
    dict | None
        Si el formato es incorrecto, retorna {'error': 'Formato de id_causa inválido'}.
        Si encuentra la causa, retorna el dict con todos los datos de la causa encontrada.
        Si no encuentra ninguna causa, retorna None.

    Ejemplo de uso:
    --------------
    causa = await get_causa_by_id("c-2025-001")
    # Corrige a "C-2025-001" y busca correctamente.
    """
    # Corrige la capitalización del primer carácter
    if id_causa and id_causa[0].islower():
        id_causa = id_causa[0].upper() + id_causa[1:]

    pattern = r'^C-\d{4}-\d{3}$'
    if not re.match(pattern, id_causa):
        return {'error': 'Formato de id_causa inválido. Debe ser C-YYYY-NNN (ej: C-2025-001)'}

    filtro = {'id_causa': id_causa}
    causa = await collection_causas.find_one(filtro, projection={'_id': 0})
    tareas = await collection_tareas.find(filtro, projection={'_id': 0}).to_list()
    if causa:
        causa['tareas'] = tareas
        return causa

    return {'error': f"No se encontro ningun registro de causa con id: {id_causa}"}

@tool
async def get_causa_by_persona(
state: Annotated[dict, InjectedState]
) -> list[dict] | None:
    """
    Busca todas las causas relacionadas con la persona.
        
    Returns:
        Lista de causas relacionadas con la persona
    """

    phone_number = state.get("phone_number")

    phone_number = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Buscamos coincidencias exactas
    filtro = {
    "partes.demandante.contacto": phone_number
    }

    proyeccion = {
        '_id': 0,
        'id_causa': 1,
        'titulo': 1,
        'tipo': 1,
        'descripcion': 1,
        'fecha_creacion': 1
    }

    return await collection_causas.find(filtro,
        projection=proyeccion).to_list(length=100)


@tool
async def change_human(
    state: Annotated[dict, InjectedState]
)->str:
    """
    Se llama cuando se necesita pasar el control al equipo humano
    """
    try:
        phone_number = state.get("phone_number")

        await lock_bot(phone_number)
        return "lock"
    except Exception as e:
        return f"Error: {e}"


tools_especialista = [change_human]
tools_principal = [get_causa_by_id, get_causa_by_persona, change_human]

