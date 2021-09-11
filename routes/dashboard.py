from fastapi import APIRouter
from fastapi.param_functions import Depends
from starlette.requests import Request
from dependencies import get_user
import math
router = APIRouter()

def pterodactyl(config):
    if config['pterodactyl']['domain'].endswith('/'):
        pterodactyl = f"{config['pterodactyl']['domain']}"
    else:
        pterodactyl = f"{config['pterodactyl']['domain']}/"
    return pterodactyl
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0MB"
   size_name = ("MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

@router.get("/")
async def dashboard_get(request: Request, user = Depends(get_user)):
    ptero = pterodactyl(request.app.config)
    async with request.app.session.get(f"{ptero}api/application/users/{user['pterodactyl']['id']}?include=servers", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        servers = req['attributes']['relationships']['servers']['data']
    for server in servers:
        server['attributes']['limits']['memory'] = convert_size(server['attributes']['limits']['memory']) if server['attributes']['limits']['memory'] != 0 else "Unlimited"
        server['attributes']['limits']['disk'] = convert_size(server['attributes']['limits']['disk']) if server['attributes']['limits']['disk'] != 0 else "Unlimited"
        server['attributes']['limits']['cpu'] = server['attributes']['limits']['cpu'] if server['attributes']['limits']['cpu'] != 0 else "Unlimited"  
    return request.app.templates.TemplateResponse("dashboard/dash.html", {"request": request, "user": user, "servers": servers, "panel": ptero})