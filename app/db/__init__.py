from pymongo import AsyncMongoClient
from ..core.config import config

# client
client = AsyncMongoClient(config.mongodb_uri)

# Database
db = client[config.name_db_mongo]

# Collections
collection_causas = db["causas"]
collection_tareas = db["tareas"]
collection_conversation_state = db["conversation_state"]
collection_langgraph_checkpoints = db["langgraph_checkpoints"]