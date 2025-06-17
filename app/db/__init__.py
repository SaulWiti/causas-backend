from pymongo import AsyncMongoClient
from ..core.config import config

# client
client = AsyncMongoClient(config.mongodb_uri)

# Database
db = client[config.name_db_mongo]

# Collections
collection_causas = db["causas"]
