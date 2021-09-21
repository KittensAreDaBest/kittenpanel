from fastapi import APIRouter
from fastapi.param_functions import Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse
from dependencies import get_user
import math
router = APIRouter()

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0MB"
   size_name = ("MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def resourcesUsed(servers):
    cpu = 0
    ram = 0
    disk = 0 
    backups = 0 
    ports = 0
    databases = 0
    slots = 0
    for server in servers:
        cpu += server['attributes']['limits']['cpu']
        ram += server['attributes']['limits']['memory']
        disk += server['attributes']['limits']['disk']
        backups += server['attributes']['feature_limits']['backups']
        if server['attributes']['feature_limits']['allocations'] != 0:
            ports += server['attributes']['feature_limits']['allocations'] - 1
        databases += server['attributes']['feature_limits']['databases']
        slots += 1
    return {
        'cpu': cpu,
        'ram': ram,
        'disk': disk,
        'backups': backups,
        'ports': ports,
        'databases': databases,
        'servers': slots
    }

def resourcesTotal(user, plan):
    cpu = user['resources']['cpu']
    ram = user['resources']['ram']
    disk = user['resources']['disk']
    backups = user['resources']['backups']
    ports = user['resources']['ports']
    databases = user['resources']['database']
    servers = user['resources']['servers']
    cpu += plan['resources']['cpu']
    ram += plan['resources']['ram']
    disk += plan['resources']['disk']
    backups += plan['resources']['backups']
    ports += plan['resources']['ports']
    databases += plan['resources']['database']
    servers += plan['resources']['servers']
    return {
        'cpu': cpu,
        'ram': ram,
        'disk': disk,
        'backups': backups,
        'ports': ports,
        'databases': databases,
        'servers': servers
    }

@router.get("/")
async def dashboard_get(request: Request, user = Depends(get_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    async with request.app.session.get(f"{ptero}api/application/users/{user['pterodactyl']['id']}?include=servers", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        servers = req['attributes']['relationships']['servers']['data']
    for server in servers:
        server['attributes']['limits']['memory'] = convert_size(server['attributes']['limits']['memory']) if server['attributes']['limits']['memory'] != 0 else "Unlimited"
        server['attributes']['limits']['disk'] = convert_size(server['attributes']['limits']['disk']) if server['attributes']['limits']['disk'] != 0 else "Unlimited"
        server['attributes']['limits']['cpu'] = server['attributes']['limits']['cpu'] if server['attributes']['limits']['cpu'] != 0 else "Unlimited"  
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("dashboard/dash.html", {"request": request, "user": user, "servers": servers, "panel": ptero, "config": config})

@router.get("/shop")
async def shop_get(request: Request, user = Depends(get_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    async with request.app.session.get(f"{ptero}api/application/users/{user['pterodactyl']['id']}?include=servers", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        servers = req['attributes']['relationships']['servers']['data']
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    plan = await db.plans.find_one({"_id": user['plan']})
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("dashboard/shop.html", {"request": request, "user": user, "config": config, "resourcesUsed": resourcesUsed(servers), "resourcesTotal": resourcesTotal(user, plan), "config": config})

@router.get("/server/create")
async def create_get(request: Request, user = Depends(get_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    async with request.app.session.get(f"{ptero}api/application/users/{user['pterodactyl']['id']}?include=servers", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        servers = req['attributes']['relationships']['servers']['data']
        resources = resourcesUsed(servers)
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    plan = await db.plans.find_one({"_id": user['plan']})
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("dashboard/server/create.html", {"request": request, "user": user, "resourcesUsed": resources, "resourcesTotal": resourcesTotal(user, plan), "config": config})

@router.get("/server/edit/{server_id}")
async def create_get(request: Request, server_id, user = Depends(get_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    async with request.app.session.get(f"{ptero}api/application/users/{user['pterodactyl']['id']}?include=servers", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        servers = req['attributes']['relationships']['servers']['data']
        resources = resourcesUsed(servers)

    editServer = None
    for server in servers:
        if server['attributes']['identifier'] == server_id:
            editServer = server['attributes']
    if not editServer:
        return RedirectResponse(url="/", status_code=302)
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    plan = await db.plans.find_one({"_id": user['plan']})
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("dashboard/server/edit.html", {"request": request, "user": user, "server": editServer, "resourcesUsed": resources, "resourcesTotal": resourcesTotal(user, plan), "config": config})

@router.get("/panel")
async def panel_get(request: Request, user = Depends(get_user)):
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("dashboard/panel.html", {"request": request, "user": user, "config": config})
