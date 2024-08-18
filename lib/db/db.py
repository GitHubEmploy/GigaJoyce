import os
from dotenv import load_dotenv
import motor.motor_asyncio
import discord
from discord.ext import commands

load_dotenv()

MONGODB_TOKEN = os.getenv("MONGODB_TOKEN")

class MongoDBAsyncORM:
    def __init__(self, uri, db_name="database"):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    async def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(document)
        return result.inserted_id

    async def insert_many(self, collection_name, documents):
        collection = self.get_collection(collection_name)
        result = await collection.insert_many(documents)
        return result.inserted_ids

    async def find_one(self, collection_name, query, projection=None):
        collection = self.get_collection(collection_name)
        return await collection.find_one(query, projection)

    async def find(self, collection_name, query, projection=None):
        collection = self.get_collection(collection_name)
        cursor = collection.find(query, projection)
        return await cursor.to_list(length=None)

    async def update_one(self, collection_name, query, update, upsert=False):
        collection = self.get_collection(collection_name)
        result = await collection.update_one(query, {"$set": update}, upsert=upsert)
        return result.modified_count

    async def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result.deleted_count

    async def count_documents(self, collection_name, query={}):
        collection = self.get_collection(collection_name)
        return await collection.count_documents(query)

    async def list_collections(self):
        return await self.db.list_collection_names()

    async def close(self):
        self.client.close()
        print('Closed MongoDB connection')
        