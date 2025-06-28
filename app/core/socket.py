from fastapi import WebSocket
import asyncio
from fastapi.encoders import jsonable_encoder
from ..schemas.socket import MessageSocket

# Usamos el MessageSocket del esquema existente
SocketMessage = MessageSocket

class ConnectionManager:
    def __init__(self, connection_timeout: int = 300):
        self.active_connections: list[WebSocket] = []
        self.connection_timeout = connection_timeout
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:
        """Acepta una nueva conexión WebSocket.
        """
        await websocket.accept()
        async with self._lock:
            if websocket not in self.active_connections:
                self.active_connections.append(websocket)

    async def disconnect(self, connection: WebSocket, reason: str = "Desconexión solicitada") -> bool:
        # Verificar si la conexión existe (sin lock para evitar deadlock)
        async with self._lock:
            if connection not in self.active_connections:
                return False
        
        # Cerrar la conexión
        try:
            await connection.close(code=1000, reason=reason)
        except Exception as e:
            print(f"Error al cerrar WebSocket: {e}")
            return False
        finally:
            # Asegurarse de remover la conexión incluso si falla el cierre
            async with self._lock:
                try:
                    self.active_connections.remove(connection)
                    print(f"Conexión cerrada: {connection} - Razón: {reason}")
                except ValueError:
                    # La conexión ya fue removida
                    pass
        return True
        
    async def send_message(
        self,   
        message: SocketMessage,
        websocket: WebSocket
    ) -> bool:
        """Envía un mensaje a una conexión específica.
        """
        try:
            await websocket.send_json(
                jsonable_encoder(message)
            )
            return True
        except Exception as e:
            print(f"Error enviando mensaje a {websocket}: {e}")
            await self.disconnect(websocket, "Error al enviar mensaje")
            return False

    async def broadcast(
        self, 
        message: SocketMessage,
    ) -> int:
        """Envía un mensaje a todas las conexiones activas."""
        # Obtener una copia de las conexiones bajo lock
        async with self._lock:
            if not self.active_connections:
                return 0
            connections = list(self.active_connections)
        
        success_count = 0
        dead_connections = []
        
        # Enviar mensaje a todas las conexiones
        for connection in connections:
            try:
                await connection.send_json(jsonable_encoder(message))
                success_count += 1
            except Exception as e:
                print(f"Error en broadcast a {connection}: {e}")
                dead_connections.append(connection)
        
        # Limpiar conexiones muertas fuera del lock
        for dead in dead_connections:
            await self.disconnect(dead, "Error en broadcast")
            
        return success_count
    
    async def cleanup_inactive_connections(self) -> int:
        """Método obsoleto. Se mantiene por compatibilidad."""
        return 0

    async def close_all_connections(self) -> None:
        """Cierra todas las conexiones activas."""
        # Obtener copia de las conexiones bajo lock
        async with self._lock:
            connections = list(self.active_connections)
        
        # Cerrar conexiones fuera del lock
        for connection in connections:
            await self.disconnect(connection, "Servidor cerrando")

    async def get_connection_count(self) -> int:
        """Devuelve el número de conexiones activas."""
        async with self._lock:
            return len(self.active_connections)

    async def close(self):
        """Cierra todas las conexiones de manera segura.
        
        Debe ser llamado al detener la aplicación.
        """
        await self.close_all_connections()

# Instancia global
manager = ConnectionManager()