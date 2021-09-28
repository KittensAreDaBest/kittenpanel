from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from models.admin import config, location
from dependencies import get_admin_user
import uuid
router = APIRouter(prefix="/api/admin")

@router.post("/location/create")
async def admin_api_location_create_post(request: Request, data: location.Location, user = Depends(get_admin_user)):
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    if data.name == "":
        return JSONResponse({"code": 422, "message": "Name is required"}, status_code=422)
    locations = await db.locations.find_one({"pterodactyl": data.pterodactyl})
    if locations is not None:
        return JSONResponse({"code": 422, "message": "Location already exists"}, status_code=422)
    checkname = await db.locations.find_one({"name": data.name})
    if checkname is not None:
        return JSONResponse({"code": 422, "message": "Name already exists"}, status_code=422)
    await db.locations.insert_one({
        "_id": str(uuid.uuid4()),
        "name": data.name,
        "pterodactyl": data.pterodactyl,
        "plans": data.allowed_plans,
        "types": data.allowed_eggs
    })
    return JSONResponse({"code": 200, "message": "Added Location"})

@router.delete("/location/delete/{id}")
async def admin_api_location_delete(request: Request, id: str, user = Depends(get_admin_user)):
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    location = await db.locations.find_one({"_id": id})
    if location is None:
        return JSONResponse({"code": 404, "message": "Location not found"}, status_code=404)
    await db.locations.delete_one({"_id": id})
    return JSONResponse({"code": 200, "message": "Location deleted"})

@router.post("/config/shop")
async def admin_api_config_shop_post(request: Request, data: config.ShopConfig, user = Depends(get_admin_user)):
    if data.shop_cpu:
        if not data.shop_cpu_price:
            return JSONResponse({"code": 422, "message": "CPU Price is required"}, status_code=422)
        if not data.shop_cpu_min:
            return JSONResponse({"code": 422, "message": "Min CPU Purchase is required"}, status_code=422)
    if data.shop_ram:
        if not data.shop_ram_price:
            return JSONResponse({"code": 422, "message": "RAM Price is required"}, status_code=422)
        if not data.shop_ram_min:
            return JSONResponse({"code": 422, "message": "Min RAM Purchase is required"}, status_code=422)
    if data.shop_hdd:
        if not data.shop_hdd_price:
            return JSONResponse({"code": 422, "message": "HDD Price is required"}, status_code=422)
        if not data.shop_hdd_min:
            return JSONResponse({"code": 422, "message": "Min HDD Purchase is required"}, status_code=422)
    if data.shop_backups:
        if not data.shop_backups_price:
            return JSONResponse({"code": 422, "message": "Backups Price is required"}, status_code=422)
    if data.shop_port:
        if not data.shop_port_price:
            return JSONResponse({"code": 422, "message": "Port Price is required"}, status_code=422)
    if data.shop_database:
        if not data.shop_database_price:
            return JSONResponse({"code": 422, "message": "Database Price is required"}, status_code=422)
    if data.shop_slots:
        if not data.shop_slots_price:
            return JSONResponse({"code": 422, "message": "Slots Price is required"}, status_code=422)
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    db.config.update_one({"_id": 1}, {"$set": {
        "shop": {
            "codes": data.promo_code,
            "cpu": {
                "enabled": data.shop_cpu,
                "price": data.shop_cpu_price,
                "min": data.shop_cpu_min
            },
            "ram": {
                "enabled": data.shop_ram,
                "price": data.shop_ram_price,
                "min": data.shop_ram_min
            },
            "disk": {
                "enabled": data.shop_hdd,
                "price": data.shop_hdd_price,
                "min": data.shop_hdd_min
            },
            "backups": {
                "enabled": data.shop_backups,
                "price": data.shop_backups_price
            },
            "databases": {
                "enabled": data.shop_database,
                "price": data.shop_backups_price
            },
            "servers": {
                "enabled": data.shop_slots,
                "price": data.shop_slots_price
            },
            "ports": {
                "enabled": data.shop_port,
                "price": data.shop_port_price
            },
        }
    }})
    return JSONResponse({"code": 200, "message": "Updated Shop Config"})
@router.post("/config/server")
async def admin_api_config_server_post(request: Request, data: config.ServerConfig ,user = Depends(get_admin_user)):
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    await db.config.update_one({"_id": 1}, {"$set": {"server": {"creation": data.server_creation, "deletion": data.server_deletion, "update": data.server_editing}}})
    return JSONResponse({"code": 200, "message": "Updated Server Config"})

@router.post("/config/user")
async def admin_api_config_user_post(request: Request, data: config.UserConfig ,user = Depends(get_admin_user)):
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    await db.config.update_one({"_id": 1}, {"$set": {"user": {"creation": data.user_creation}}})
    return JSONResponse({"code": 200, "message": "Updated User Config"})