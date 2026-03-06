"""
MongoDB Service for Dynamic Data Storage
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List, Optional
from app.config import settings
from app.utils.logger import logger


class MongoDBService:
    """Service for MongoDB operations"""
    
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client (singleton)"""
        if cls._client is None:
            try:
                cls._client = MongoClient(settings.MONGODB_URL)
                cls._db = cls._client[settings.MONGODB_DB_NAME]
                # Test connection
                cls._client.admin.command('ping')
                logger.info("MongoDB connection established")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
                raise
        return cls._client
    
    @classmethod
    def get_collection(cls, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if cls._db is None:
            cls.get_client()
        return cls._db[collection_name]
    
    @classmethod
    def insert_document(
        cls,
        collection_name: str,
        operator_id: int,
        external_id: str,
        data: Dict[str, Any],
        schema_version: int = 1
    ) -> str:
        """Insert a document into MongoDB"""
        collection = cls.get_collection(collection_name)
        
        document = {
            "operator_id": operator_id,
            "external_id": external_id,
            "schema_version": schema_version,
            "data": data,
            "metadata": {
                "created_at": None,  # Will be set by MongoDB
                "updated_at": None
            }
        }
        
        result = collection.insert_one(document)
        logger.debug(f"Inserted document", collection=collection_name, id=str(result.inserted_id))
        return str(result.inserted_id)
    
    @classmethod
    def update_document(
        cls,
        collection_name: str,
        operator_id: int,
        external_id: str,
        data: Dict[str, Any],
        schema_version: Optional[int] = None
    ) -> bool:
        """Update a document in MongoDB"""
        collection = cls.get_collection(collection_name)
        
        filter_query = {
            "operator_id": operator_id,
            "external_id": external_id
        }
        
        update_data = {
            "$set": {
                "data": data,
                "metadata.updated_at": None  # MongoDB will set current time
            }
        }
        
        if schema_version:
            update_data["$set"]["schema_version"] = schema_version
        
        result = collection.update_one(filter_query, update_data, upsert=True)
        return result.modified_count > 0 or result.upserted_id is not None
    
    @classmethod
    def get_document(
        cls,
        collection_name: str,
        operator_id: int,
        external_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a document from MongoDB"""
        collection = cls.get_collection(collection_name)
        
        document = collection.find_one({
            "operator_id": operator_id,
            "external_id": external_id
        })
        
        return document
    
    @classmethod
    def bulk_insert(
        cls,
        collection_name: str,
        documents: List[Dict[str, Any]]
    ) -> int:
        """Bulk insert documents"""
        if not documents:
            return 0
        
        collection = cls.get_collection(collection_name)
        result = collection.insert_many(documents)
        logger.info(f"Bulk inserted {len(result.inserted_ids)} documents", collection=collection_name)
        return len(result.inserted_ids)
    
    @classmethod
    def find_documents(
        cls,
        collection_name: str,
        operator_id: int,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find documents with filter"""
        collection = cls.get_collection(collection_name)
        
        query = {"operator_id": operator_id}
        if filter_query:
            query.update(filter_query)
        
        cursor = collection.find(query).limit(limit).skip(skip)
        return list(cursor)
    
    @classmethod
    def count_documents(
        cls,
        collection_name: str,
        operator_id: int,
        filter_query: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count documents"""
        collection = cls.get_collection(collection_name)
        
        query = {"operator_id": operator_id}
        if filter_query:
            query.update(filter_query)
        
        return collection.count_documents(query)
    
    @classmethod
    def create_indexes(cls, collection_name: str) -> None:
        """Create indexes for a collection"""
        collection = cls.get_collection(collection_name)
        
        # Create indexes
        collection.create_index([("operator_id", 1), ("external_id", 1)], unique=True)
        collection.create_index([("operator_id", 1)])
        collection.create_index([("operator_id", 1), ("schema_version", 1)])
