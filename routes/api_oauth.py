from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import quote
import uuid
import time
router = APIRouter(prefix="/api/oauth")

@router.get("/login", response_class=RedirectResponse)
async def login(request: Request):
    conf = request.app.config
    if conf['forcejoin']['enabled']:
        scopes = 'identify email guilds guilds.join'
    else:
        scopes = 'identify email'
    if conf['oauth2']['domain'].endswith('/'):
        redirect_url = f"{conf['oauth2']['domain']}api/oauth/callback"
    else:
        redirect_url = f"{conf['oauth2']['domain']}/api/oauth/callback"
    return RedirectResponse(f"https://discord.com/api/oauth2/authorize?client_id={conf['oauth2']['id']}&scope={quote(scopes)}&response_type=code&prompt=none&redirect_uri={quote(redirect_url)}", status_code=302)

@router.get("/callback", response_class=RedirectResponse)
async def callback(request: Request, code: str):
    conf = request.app.config
    if conf['forcejoin']['enabled']:
        scopes = 'identify email guilds guilds.join'
    else:
        scopes = 'identify email'
    if conf['oauth2']['domain'].endswith('/'):
        redirect_url = f"{conf['oauth2']['domain']}api/oauth/callback"
    else:
        redirect_url = f"{conf['oauth2']['domain']}/api/oauth/callback"
    async with request.app.session.post("https://discord.com/api/oauth2/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"client_id": conf['oauth2']['id'], "client_secret": conf['oauth2']['secret'], "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_url}) as resp:
        resp = await resp.json()
        try:
            if resp["error"]:
                if resp['error'] == 'invalid_request':
                    return RedirectResponse("/api/oauth/login", status_code=302)
                return JSONResponse({"error": "An error occurred"}, status_code=400)
        except KeyError:
            pass
        missingscopes = None
        for i in scopes.split(" "):
            if i not in resp['scope'].split(" "):
                missingscopes += i 
        if missingscopes:
            return JSONResponse({"error": f"Missing scopes: {missingscopes}"}, status_code=400)
    async with request.app.session.get("https://discord.com/api/users/@me", headers={"Authorization": "Bearer " + resp["access_token"]}) as dresp:
        rr = await dresp.json()
        if not rr["verified"]:
            return JSONResponse({"error": "Discord Email not verified"}, status_code=403)
    session = str(uuid.uuid4())
    db = await request.app.database.get_db_client()
    await db.kittenpanel.sessions.insert_one({"_id": session, "user_id": rr["id"], "accesstoken": resp["access_token"], "expires": time.time() + 518400})
    if not await db.kittenpanel.users.find_one({"_id": rr["id"]}):
        if conf['pterodactyl']['domain'].endswith('/'):
            pterodactyl = f"{conf['pterodactyl']['domain']}"
        else:
            pterodactyl = f"{conf['pterodactyl']['domain']}/"
        async with request.app.session.get(pterodactyl + "api/application/users?include=servers&filter[email]=" + quote(rr['email']), headers={"Authorization": "Bearer " + conf['pterodactyl']['key']}) as resp:
            data = await resp.json()
            if data['meta']['pagination']['total'] == 0:
                async with request.app.session.post(pterodactyl + "api/application/users", json={"username": str(rr['id']), "email": rr['email'], "first_name": rr['username'], "last_name": '#' + rr['discriminator']}) as resp:
                    dd = await resp.json()
                    await db.kittenpanel.users.insert_one({
                        "_id": rr['id'], 
                        "pterodactyl": dd['attributes']['id'], 
                        "disabled": False,
                        "plan": 1,
                        "resources": {
                            "cpu": 0,
                            "ram": 0,
                            "disk": 0,
                            "servers": 0,
                            "backups": 0,
                            "ports": 0,
                            "credits": 0
                        }
                    })
            user = data['data'][0]['attributes']
            if user['email'] != rr['email']:
                raise Exception("Well this shouldnt be happening since its being filtered. Raising exception to prevent any security problems")
            await db.kittenpanel.users.insert_one({
                "_id": rr['id'], 
                "pterodactyl": user['id'], 
                "disabled": False,
                "plan": 1,
                "resources": {
                    "cpu": 0,
                    "ram": 0,
                    "disk": 0,
                    "servers": 0,
                    "backups": 0,
                    "ports": 0,
                    "credits": 0
                }
            })        
    response = RedirectResponse("/dashboard/", status_code=302)
    response.set_cookie(key="kittenpanel_sessionid", value=session)
    return response