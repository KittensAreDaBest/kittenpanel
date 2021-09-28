from fastapi import APIRouter, Request, Depends
from dependencies import get_admin_user

router = APIRouter(prefix="/admin")
def pterodactyl(config):
    if config['pterodactyl']['domain'].endswith('/'):
        pterodactyl = f"{config['pterodactyl']['domain']}"
    else:
        pterodactyl = f"{config['pterodactyl']['domain']}/"
    return pterodactyl

@router.get("/")
async def admin_dash_get(request: Request, user = Depends(get_admin_user)):
    return request.app.templates.TemplateResponse("admin/dash.html", {"request": request, "user": user})

@router.get('/users')
async def admin_users_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/user/view.html", {"request": request, "user": user, "panel": ptero})

@router.get('/codes')
async def admin_codes_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/codes/view.html", {"request": request, "user": user, "panel": ptero})

@router.get('/codes/create')
async def admin_codes_create_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/codes/create.html", {"request": request, "user": user, "panel": ptero})


@router.get('/eggs')
async def admin_types_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/eggs/view.html", {"request": request, "user": user, "panel": ptero})

@router.get('/eggs/create')
async def admin_types_create_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/eggs/create.html", {"request": request, "user": user, "panel": ptero})

@router.get('/locations')
async def admin_locations_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    locations = await db.locations.find().to_list(None)
    for location in locations:
        types = ""
        plans = ""
        for type in location['types']:
            print(type)
            tl = await db.servertypes.find_one({'_id': type})
            print(tl)
            if tl:
                types += f", {tl['name']}" if types != "" else tl['name']
        for plan in location['plans']:
            pl = await db.plans.find_one({'_id': plan})
            if pl:
                plans += f", {pl['name']}" if plans != "" else pl['name']
        location['plans'] = plans
        print(plans)
        location['types'] = types
    return request.app.templates.TemplateResponse("admin/locations/view.html", {"request": request, "user": user, "panel": ptero, "locations": locations})

@router.get('/locations/create')
async def admin_locations_create_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    async with request.app.session.get(f"{ptero}api/application/locations", headers={"Authorization": f"Bearer {request.app.config['pterodactyl']['key']}"}) as response:
        req = await response.json()
        locations = req['data']
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    plans = await db.plans.find().to_list(None)
    types = await db.servertypes.find().to_list(None)
    return request.app.templates.TemplateResponse("admin/locations/create.html", {"request": request, "user": user, "panel": ptero, "plans": plans, "types": types, "locations": locations})

@router.get('/config')
async def admin_config_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    config = await db.config.find_one({"_id": 1})
    return request.app.templates.TemplateResponse("admin/config.html", {"request": request, "user": user, "panel": ptero, "config": config})

@router.get('/plans')
async def admin_plans_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/plans/view.html", {"request": request, "user": user, "panel": ptero})

@router.get('/plans/create')
async def admin_plans_create_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/plans/create.html", {"request": request, "user": user, "panel": ptero})