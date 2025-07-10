from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect
)
import json
from typing import Dict, Any
import time
from ..core.socket import manager
from ..core.security import validate_api_key

router = APIRouter(
    tags=["Socket"],
    #dependencies=[Depends(validate_api_key)]
)

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    last_ping = time.time()
    
    try:
        while True:
            # Recibir mensaje
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Manejar mensaje de ping
                if isinstance(message, dict) and message.get('type') == 'ping':
                    # Enviar pong de vuelta
                    await websocket.send_json({
                        'type': 'pong',
                        'timestamp': message.get('timestamp')
                    })
                    last_ping = time.time()
                    continue
                    
            except json.JSONDecodeError:
                # Si no es un JSON válido, lo ignoramos
                continue
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await manager.disconnect(websocket)
        except:
            pass
    finally:
        # Asegurarse de que la conexión se cierre correctamente
        try:
            await websocket.close()
        except:
            pass