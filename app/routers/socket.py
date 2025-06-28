from fastapi import (
    WebSocket, WebSocketDisconnect
)
from fastapi import (
    APIRouter, Depends
    )
from ..core.socket import manager
from ..core.security import validate_api_key

router = APIRouter(
    tags=["Socket"],
    #dependencies=[Depends(validate_api_key)]
)

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantener la conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await manager.disconnect(websocket, "Error interno del servidor")