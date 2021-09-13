from fastapi import APIRouter, Request
from fastapi.param_functions import Depends
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import quote
from dependencies import get_user_session
import uuid
import time
router = APIRouter()

@router.get("/logout")
async def logout(request: Request, session = Depends(get_user_session)):
    conf = request.app.config
    await request.app.session.post("https://discord.com/api/oauth2/token/revoke", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"client_id": conf['oauth2']['id'], "client_secret": conf['oauth2']['secret'], "token": session['accesstoken']})
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]

    await db.sessions.delete_one({"_id": session['_id']})
    response = RedirectResponse(conf['mainsite'], status_code=302)
    response.delete_cookie(key="kittenpanel_sessionid")
    return response

@router.get("/login", response_class=RedirectResponse)
async def login(request: Request):
    conf = request.app.config
    if conf['forcejoin']['enabled']:
        scopes = 'identify email guilds guilds.join'
    else:
        scopes = 'identify email'
    if conf['oauth2']['domain'].endswith('/'):
        redirect_url = f"{conf['oauth2']['domain']}callback"
    else:
        redirect_url = f"{conf['oauth2']['domain']}/callback"
    return RedirectResponse(f"https://discord.com/api/oauth2/authorize?client_id={conf['oauth2']['id']}&scope={quote(scopes)}&response_type=code&prompt=none&redirect_uri={quote(redirect_url)}", status_code=302)


@router.get("/callback", response_class=RedirectResponse)
async def callback(request: Request, code: str):
    conf = request.app.config
    if conf['forcejoin']['enabled']:
        scopes = 'identify email guilds guilds.join'
    else:
        scopes = 'identify email'
    if conf['oauth2']['domain'].endswith('/'):
        redirect_url = f"{conf['oauth2']['domain']}callback"
    else:
        redirect_url = f"{conf['oauth2']['domain']}/callback"
    async with request.app.session.post("https://discord.com/api/oauth2/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"client_id": conf['oauth2']['id'], "client_secret": conf['oauth2']['secret'], "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_url}) as resp:
        resp = await resp.json()
        try:
            if resp["error"]:
                if resp['error'] == 'invalid_request':
                    return RedirectResponse("/login", status_code=302)
                return JSONResponse({"error": "An error occurred"}, status_code=500)
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
    db = db[request.app.config['database']['database']]
    await db.sessions.insert_one({"_id": session, "user_id": rr["id"], "accesstoken": resp["access_token"], "expires": time.time() + 518400})
    if conf['pterodactyl']['domain'].endswith('/'):
        pterodactyl = f"{conf['pterodactyl']['domain']}"
    else:
        pterodactyl = f"{conf['pterodactyl']['domain']}/"
    if not await db.users.find_one({"_id": rr["id"]}):
        async with request.app.session.get(pterodactyl + "api/application/users?include=servers&filter[email]=" + quote(rr['email']), headers={"Authorization": "Bearer " + conf['pterodactyl']['key']}) as resp:
            data = await resp.json()
            if data['meta']['pagination']['total'] == 0:
                async with request.app.session.post(pterodactyl + "api/application/users", json={"username": str(rr['id']), "email": rr['email'], "first_name": rr['username'], "last_name": '#' + rr['discriminator']}) as resp:
                    dd = await resp.json()
                    await db.users.insert_one({
                        "_id": rr['id'], 
                        "disabled": False,
                        "plan": 1,
                        "resources": {
                            "cpu": 0,
                            "ram": 0,
                            "disk": 0,
                            "servers": 0,
                            "backups": 0,
                            "ports": 0,
                            "database": 0,
                            "credits": 0
                        },
                        "discord": {
                            "id": rr["id"],
                            "username": rr["username"],
                            "discriminator": rr["discriminator"],
                            "avatar": rr["avatar"],
                            "email": rr["email"]
                        },
                        "pterodactyl": {
                            "id": dd['id'],
                            "username": dd['username'],
                            "email": dd['email'],
                            "admin": dd['root_admin']
                        },
                    })
            else:
                user = data['data'][0]['attributes']
                if user['email'] != rr['email']:
                    raise Exception("Well this shouldnt be happening since its being filtered. Raising exception to prevent any security problems")
                await db.users.insert_one({
                    "_id": rr['id'], 
                    "disabled": False,
                    "plan": 1,
                    "resources": {
                        "cpu": 0,
                        "ram": 0,
                        "disk": 0,
                        "servers": 0,
                        "backups": 0,
                        "ports": 0,
                        "database": 0,
                        "credits": 0
                    },
                    "discord": {
                        "id": rr["id"],
                        "username": rr["username"],
                        "discriminator": rr["discriminator"],
                        "avatar": rr["avatar"],
                        "email": rr["email"]
                    },
                    "pterodactyl": {
                        "id": user['id'],
                        "username": user['username'],
                        "email": user['email'],
                        "admin": user['root_admin']
                    }
                })     
    else:
        discord = {
            "id": rr["id"],
            "username": rr["username"],
            "discriminator": rr["discriminator"],
            "avatar": rr["avatar"],
            "email": rr["email"]
        }
        user = await db.users.find_one({"_id": rr["id"]})
        async with request.app.session.get(pterodactyl + "api/application/users/" + str(user['pterodactyl']['id']), headers={"Authorization": "Bearer " + conf['pterodactyl']['key']}) as resp:
            pterodata = await resp.json()
        user = pterodata['attributes']
        if user['email'] != rr['email']:
            raise Exception("Well this shouldnt be happening since its being filtered. Raising exception to prevent any security problems")
        pterodactyl = {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "admin": user['root_admin']
        }
        await db.users.update_one({"_id": rr["id"]}, {"$set": {"discord": discord, "pterodactyl": pterodactyl}})   
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="kittenpanel_sessionid", value=session, httponly=True)
    return response