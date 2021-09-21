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
    return request.app.templates.TemplateResponse("admin/user.html", {"request": request, "user": user, "panel": ptero})

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
    return request.app.templates.TemplateResponse("admin/locations/view.html", {"request": request, "user": user, "panel": ptero})

@router.get('/locations/create')
async def admin_locations_create_get(request: Request, user = Depends(get_admin_user)):
    ptero = f"{request.app.config['pterodactyl']['domain']}" if request.app.config['pterodactyl']['domain'].endswith('/') else f"{request.app.config['pterodactyl']['domain']}/"
    return request.app.templates.TemplateResponse("admin/locations/create.html", {"request": request, "user": user, "panel": ptero})

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