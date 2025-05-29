import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def get_database():
    """Get database instance"""
    return db.database


async def connect_to_mongo():
    """Create database connection."""
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        db.client = AsyncIOMotorClient(mongodb_uri)
        db.database = db.client.todoapp
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


# Task collection operations
class TaskRepository:
    def __init__(self, database):
        self.collection = database.tasks
    
    async def create_task(self, task_data: dict) -> dict:
        """Create a new task"""
        result = await self.collection.insert_one(task_data)
        task_data["_id"] = result.inserted_id
        return task_data
    
    async def get_all_tasks(self) -> list:
        """Get all tasks"""
        cursor = self.collection.find({})
        tasks = await cursor.to_list(length=None)
        return tasks
    
    async def get_task_by_id(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        from bson import ObjectId
        try:
            task = await self.collection.find_one({"_id": ObjectId(task_id)})
            return task
        except Exception:
            return None
    
    async def update_task(self, task_id: str, update_data: dict) -> Optional[dict]:
        """Update task by ID"""
        from bson import ObjectId
        try:
            # Add updated_at timestamp
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await self.get_task_by_id(task_id)
            return None
        except Exception:
            return None
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete task by ID"""
        from bson import ObjectId
        try:
            result = await self.collection.delete_one({"_id": ObjectId(task_id)})
            return result.deleted_count > 0
        except Exception:
            return False


async def get_task_repository():
    """Get task repository instance"""
    database = await get_database()
    return TaskRepository(database)
