import os
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

MONGODB_TOKEN = os.getenv("MONGODB_TOKEN")

class MongoDBAsyncORM:
    def __init__(self, uri, db_name="database"):
        """
        Initialize the MongoDBAsyncORM instance.
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        """
        Get a specific collection by name.
        """
        return self.db[collection_name]
    
    async def create_index(self, collection_name, keys, unique=False):
        """
        Create an index on the specified collection.

        Args:
            collection_name (str): The name of the collection.
            keys (list of tuples): List of key-direction pairs for the index (e.g., [("id", 1), ("guildId", 1)]).
            unique (bool): Whether the index should enforce uniqueness.
        """
        collection = self.get_collection(collection_name)
        index_name = await collection.create_index(keys, unique=unique)
        return index_name

    async def insert_one(self, collection_name, document):
        """
        Insert a single document into a collection.
        """
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(document)
        return result.inserted_id

    async def insert_many(self, collection_name, documents):
        """
        Insert multiple documents into a collection.
        """
        collection = self.get_collection(collection_name)
        result = await collection.insert_many(documents)
        return result.inserted_ids

    async def find_one(self, collection_name, query, projection=None):
        """
        Find a single document in a collection.
        """
        collection = self.get_collection(collection_name)
        return await collection.find_one(query, projection)

    async def find(self, collection_name, query, projection=None):
        """
        Find multiple documents in a collection.
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(query, projection)
        return await cursor.to_list(length=None)

    async def update_one(self, collection_name, query, update, upsert=False):
        """
        Update a single document in a collection.
        """
        collection = self.get_collection(collection_name)

        # Se o update já contiver um operador, não encapsule novamente com $set
        if not any(key.startswith('$') for key in update.keys()):
            update = {"$set": update}

        result = await collection.update_one(query, update, upsert=upsert)
        return result.modified_count


    async def delete_one(self, collection_name, query):
        """
        Delete a single document from a collection.
        """
        collection = self.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result.deleted_count

    async def count_documents(self, collection_name, query={}):
        """
        Count the number of documents in a collection.
        """
        collection = self.get_collection(collection_name)
        return await collection.count_documents(query)

    async def list_collections(self):
        """
        List all collections in the database.
        """
        return await self.db.list_collection_names()

    async def ensure_guild_structure(self, module_name, structure):
        """
        Ensure a specific structure exists in all guild collections.

        Args:
            module_name (str): Name of the module (e.g., "XPSystem").
            structure (dict): Structure to ensure exists in the database.
        """
        guilds = await self.find("guilds", {})  # Assuming a 'guilds' collection exists
        for guild in guilds:
            guild_id = guild.get("guild_id")
            if not guild_id:
                continue

            collection_name = f"guild_{guild_id}"  # Example pattern for guild-specific collections
            existing_data = await self.find_one(collection_name, {"module_name": module_name})

            if not existing_data:
                await self.insert_one(collection_name, {
                    "module_name": module_name,
                    **structure
                })

    async def close(self):
        """
        Close the connection to the MongoDB database.
        """
        self.client.close()
        print("Closed MongoDB connection")
