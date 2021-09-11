from fastapi import Header, HTTPException, Request
from fastapi import Cookie

class AuthenticationException(Exception):
    def __init__(self, name: str):
        self.name = name

async def get_user(request: Request, kittenpanel_sessionid: str = Cookie(None)):
    if kittenpanel_sessionid is None:
        raise AuthenticationException(name="Not authenticated")
    db = await request.app.database.get_db_client()
    session = await db.kittenpanel.sessions.find_one({"_id": kittenpanel_sessionid})
    if session is None:
        raise AuthenticationException(name="Unauthorized")
    else:
        user = await db.kittenpanel.users.find_one({"_id": session["user_id"]})
        return user

async def get_user_session(request: Request, kittenpanel_sessionid: str = Cookie(None)):
    if kittenpanel_sessionid is None:
        raise AuthenticationException(name="Not authenticated")
    db = await request.app.database.get_db_client()
    session = await db.kittenpanel.sessions.find_one({"_id": kittenpanel_sessionid})
    if session is None:
        raise AuthenticationException(name="Unauthorized")
    else:
        return session