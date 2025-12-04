from __future__ import annotations

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase
import os
from functools import lru_cache


class Database:
    _instance: "Database" | None = None
    _init_done = False
        
    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError("Database singleton already created; use get_database()")
        cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = (
            os.getenv("MONGO_CURRENT_DB")
            or os.getenv("MONGO_DB")
            or "music_sheets_db"
        )

        self._client: MongoClient = MongoClient(
            self.mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        self._db: MongoDatabase = self._client[self.db_name]
        self._pieces_collection: Collection = self._db["pieces_metadata"]

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self) -> MongoDatabase:
        return self._db

    @property
    def pieces_collection(self) -> Collection:
        return self._pieces_collection


# Singleton
@lru_cache
def get_database() -> Database:
    return Database()
