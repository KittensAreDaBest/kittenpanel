from motor.motor_asyncio import AsyncIOMotorClient
import os
class MongoDB():
    def __init__(self, db: str) -> None:
        self.db_client: AsyncIOMotorClient = None
        self.db = db
    async def get_db_client(self) -> AsyncIOMotorClient:
        """Return database client instance."""
        return self.db_client

    async def connect_db(self):
        """Create database connection."""
        self.db_client = AsyncIOMotorClient(self.db)

    async def close_db(self):
        """Close database connection."""
        self.db_client.close()