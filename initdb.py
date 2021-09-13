import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
async def main():
    with open("config.json", "rb") as file:
        config = json.load(file)
    db = AsyncIOMotorClient(config["database"]["host"])
    db = db[config["database"]["database"]]
    await db.plans.insert_one({
        "_id": 1,
        "name": "Default Plan",
        "resources": {
            "cpu": 100,
            "ram": 1024,
            "disk": 2048,
            "servers": 2,
            "backups": 0,
            "ports": 0,
            "database": 0
        }
    })
    await db.locations.insert_one({
        "_id": 1,
        "name": "Default Location",
        "pterodactyl": 1
    })
    await db.servertypes.insert_one({
        "_id": 1,
        "name": "PaperMC",
        "egg": 3,
        "nest": 1
    })
asyncio.run(main())