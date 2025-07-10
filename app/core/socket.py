from fastapi import WebSocket
import asyncio
from fastapi.encoders import jsonable_encoder
from ..schemas.socket import MessageSocket
from typing import List, Dict, Any

# Usamos el MessageSocket del esquema existente
SocketMessage = MessageSocket

class ConnectionManager:
    def __init__(self, connection_timeout: int = 300):
        self.active_connections: List[WebSocket] = []
        self.connection_timeout = connection_timeout
        self._lock = asyncio.Lock()
        # Diccionario para almacenar colas de mensajes por conexión
        self.message_queues: Dict[WebSocket, asyncio.Queue] = {}
        # Tareas de procesamiento de colas
        self.processing_tasks: Dict[WebSocket, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Acepta una nueva conexión WebSocket y configura su cola de mensajes."""
        await websocket.accept()
        async with self._lock:
            if websocket not in self.active_connections:
                self.active_connections.append(websocket)
                self.message_queues[websocket] = asyncio.Queue()
                # Iniciar el procesador de mensajes para esta conexión
                self.processing_tasks[websocket] = asyncio.create_task(
                    self._process_messages(websocket)
                )

    async def _process_messages(self, websocket: WebSocket) -> None:
        """Procesa mensajes de la cola para una conexión específica."""
        queue = self.message_queues.get(websocket)
        if not queue:
            return

        while True:
            try:
                # Obtener el siguiente mensaje de la cola
                message = await queue.get()
                
                # Verificar si la conexión sigue activa
                if websocket not in self.active_connections:
                    break
                    
                # Enviar el mensaje
                try:
                    await websocket.send_json(jsonable_encoder(message))
                except Exception as e:
                    print(f"Error enviando mensaje a {websocket}: {e}")
                    await self.disconnect(websocket, "Error al enviar mensaje")
                    break
                    
                # Pequeña pausa para evitar sobrecarga
                await asyncio.sleep(0.01)
                
            except asyncio.CancelledError:
                # La tarea fue cancelada
                break
            except Exception as e:
                print(f"Error en el procesador de mensajes: {e}")
                await asyncio.sleep(1)  # Pequeña pausa antes de reintentar

    async def send_message(
        self,   
        message: Any,
        websocket: WebSocket
    ) -> bool:
        """Envía un mensaje a una conexión específica usando la cola."""
        if websocket not in self.active_connections:
            return False
            
        queue = self.message_queues.get(websocket)
        if not queue:
            return False
            
        try:
            # Agregar el mensaje a la cola
            await queue.put(message)
            return True
        except Exception as e:
            print(f"Error encolando mensaje: {e}")
            return False

    async def broadcast(
        self, 
        message: Any,
    ) -> int:
        """Envía un mensaje a todas las conexiones activas usando colas."""
        async with self._lock:
            if not self.active_connections:
                return 0
            connections = list(self.active_connections)
        
        success_count = 0
        
        # Enviar a cada conexión a través de su cola
        for connection in connections:
            try:
                if await self.send_message(message, connection):
                    success_count += 1
            except Exception as e:
                print(f"Error en broadcast a {connection}: {e}")
                await self.disconnect(connection, "Error en broadcast")
                
        return success_count

    async def disconnect(self, connection: WebSocket, reason: str = "Desconexión solicitada") -> bool:
        """Cierra una conexión y limpia sus recursos."""
        # Remover de las conexiones activas
        async with self._lock:
            if connection not in self.active_connections:
                return False
            self.active_connections.remove(connection)
            
            # Cancelar la tarea de procesamiento
            task = self.processing_tasks.pop(connection, None)
            if task:
                task.cancel()
                
            # Limpiar la cola
            self.message_queues.pop(connection, None)

        # Cerrar la conexión WebSocket
        try:
            await connection.close(code=1000, reason=reason)
            print(f"Conexión cerrada: {connection} - Razón: {reason}")
            return True
        except Exception as e:
            print(f"Error al cerrar WebSocket: {e}")
            return False

    async def close_all_connections(self) -> None:
        """Cierra todas las conexiones activas."""
        async with self._lock:
            connections = list(self.active_connections)
        
        for connection in connections:
            await self.disconnect(connection, "Servidor cerrando")

    async def get_connection_count(self) -> int:
        """Devuelve el número de conexiones activas."""
        async with self._lock:
            return len(self.active_connections)

    async def close(self):
        """Cierra todas las conexiones de manera segura."""
        await self.close_all_connections()

# Instancia global
manager = ConnectionManager()