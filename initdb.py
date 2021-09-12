import asyncio
import json
import motor
async def main():
    with open("config.json", "rb") as file:
        config = json.load(file)
    db = motor.motor_asyncio.AsyncIOMotorClient(config["mongo"]["host"])
    db = db[config["mongo"]["db"]]
    await db.plans.insert_one({
        "_id": 1,
        "name": "Default Plan",
        "resources": {
            "cpu": 0,
            "ram": 0,
            "disk": 0,
            "servers": 0,
            "backups": 0,
            "ports": 0,
            "database": 0
        }
    })
