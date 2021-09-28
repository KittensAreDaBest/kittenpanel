import asyncio
import json
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
async def main():
    with open("config.json", "rb") as file:
        config = json.load(file)
    db = AsyncIOMotorClient(config["database"]["host"])
    db = db[config["database"]["database"]]

    config = await db.config.find_one({"_id": 1})
    if config is None:
        await db.config.insert_one({
            "_id": 1,
            "name": "general",
            "server": {
                "creation": False,
                "deletion": False,
                "update": False
            }, 
            "user": {
                "creation": False
            },
            "shop": {
                "codes": False,
                "cpu": {
                    "enabled": False,
                    "price": 0,
                    "min": 20
                },
                "ram": {
                    "enabled": False,
                    "price": 0,
                    "min": 512
                },
                "disk": {
                    "enabled": False,
                    "price": 0,
                    "min": 512
                },
                "backups": {
                    "enabled": False,
                    "price": 0
                },
                "databases": {
                    "enabled": False,
                    "price": 0
                },
                "servers": {
                    "enabled": False,
                    "price": 0
                },
                "ports": {
                    "enabled": False,
                    "price": 0
                },
            }
        })
    await db.plans.insert_one({
            "_id": str(uuid.uuid4()),
            "name": "Default Plan",
            "default": True,
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
            "_id": str(uuid.uuid4()),
            "name": "Default Location",
            "pterodactyl": 1,
            "plans": [],
            "types": []
        })
    await db.servertypes.insert_one({
            "_id": str(uuid.uuid4()),
            "name": "PaperMC",
            "pterodactyl": {
                "egg": 3,
                "docker_image": "quay.io/pterodactyl/core:java",
                "environment": {
                    "SERVER_JARFILE": "server.jar",
                    "BUILD_NUMBER": "latest"
                }
            },
            "min": {
                "cpu": 1,
                "ram": 1024,
                "disk": 2048,
                "databases": None,
                "ports": None,
                "backups": None
            },
            "max": {
                "cpu": 1,
                "ram": 1024,
                "disk": 2048,
                "databases": None,
                "ports": None,
                "backups": None
            }
        })
asyncio.run(main())