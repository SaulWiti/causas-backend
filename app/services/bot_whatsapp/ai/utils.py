from typing import Any, Dict, Union
from pymongo import AsyncMongoClient
from datetime import datetime
from os import getenv
from langgraph.checkpoint.base import CheckpointMetadata
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

serde: SerializerProtocol = JsonPlusSerializer()
from app.db import (
    collection_langgraph_checkpoints,
    collection_conversation_state
)

def loads_metadata(metadata: dict[str, Any]) -> CheckpointMetadata:
    """Deserialize metadata document

    The CheckpointMetadata class itself cannot be stored directly in MongoDB,
    but as a dictionary it can. For efficient filtering in MongoDB,
    we keep dict keys as strings.

    metadata is stored in MongoDB collection with string keys and
    serde serialized keys.
    """
    if isinstance(metadata, dict):
        output = {}
        for key, value in metadata.items():
            output[key] = loads_metadata(value)
        return output

    return serde.loads(metadata)


def dumps_metadata(
    metadata: Union[CheckpointMetadata, Any],
) -> Union[bytes, Dict[str, Any]]:
    """Serialize all values in metadata dictionary.

    Keep dict keys as strings for efficient filtering in MongoDB
    """
    if isinstance(metadata, dict):
        output = {}
        for key, value in metadata.items():
            output[key] = dumps_metadata(value)
        return output

    return serde.dumps(metadata)


def datos_mini_causa(causa:dict):
    """
    Retorna un dict con los datos minimos de la causa
    """
    return {
        "id_causa": causa["id_causa"],
        "titulo": causa["titulo"],
        "descripcion": causa["descripcion"],
        "fecha_creacion": causa["fecha_creacion"],
        "fecha_ultima_actualizacion": causa["fecha_ultima_actualizacion"],
        "tipo": causa["tipo"]
    }

async def reset(
    phone_number:str
)->str:

    # Criterio de eliminación
    criterio = {"thread_id": phone_number}

    # Eliminar documentos
    _ = await collection_langgraph_checkpoints.delete_many(criterio)

    # Criterio de eliminación
    criterio = {"phone_number": phone_number}

    # Eliminar documentos
    _ = await collection_conversation_state.delete_many(criterio)

    return "Chat reiniciado correctamente"

