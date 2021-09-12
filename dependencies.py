from fastapi import Header, HTTPException, Request
from fastapi import Cookie

class AuthenticationException(Exception):
    def __init__(self, name: str, disabled: bool):
        self.name = name
        self.disabled = disabled
async def get_user(request: Request, kittenpanel_sessionid: str = Cookie(None)):
    if kittenpanel_sessionid is None:
        raise AuthenticationException(name="Not authenticated", disabled=False)
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    session = await db.sessions.find_one({"_id": kittenpanel_sessionid})
    if session is None:
        raise AuthenticationException(name="Unauthorized", disabled=False)
    else:
        user = await db.users.find_one({"_id": session["user_id"]})
        if user['disabled']:
            raise AuthenticationException(name="Account Disabled", disabled=True)

        return user

async def get_user_session(request: Request, kittenpanel_sessionid: str = Cookie(None)):
    if kittenpanel_sessionid is None:
        raise AuthenticationException(name="Not authenticated", disabled=False)
    db = await request.app.database.get_db_client()
    db = db[request.app.config['database']['database']]
    session = await db.sessions.find_one({"_id": kittenpanel_sessionid})
    if session is None:
        raise AuthenticationException(name="Unauthorized", disabled=False)
    else:
        return session