from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import JSONResponse, RedirectResponse
import uvicorn
import aiohttp
from routes import api_admin, api_client, oauth, dashboard, default
from utils import mongodb
from dependencies import AuthenticationException
import subprocess
import os
import sys
with open("config.json", "rb") as file:
    config = json.load(file)

app = FastAPI(title=config['appname'], docs_url="/api/docs", redoc_url="/api/docs")
app.config = config

app.mount("/static", StaticFiles(directory="static"), name="static")

app.database = mongodb.MongoDB(config['database']['host'])
app.session = aiohttp.ClientSession()

app.add_event_handler("startup", app.database.connect_db)
app.add_event_handler("shutdown", app.database.close_db)
app.templates = Jinja2Templates(directory="templates")

@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    if exc.disabled:
        return JSONResponse({"code": 403, "message": "Your account is disabled"})
    return RedirectResponse(url="/login", status_code=302)

routes = [api_admin, api_client, oauth, dashboard, default]
for route in routes:
    app.include_router(route.router)


if __name__ == "__main__":
    print(f"""\
██   ██ ██ ████████ ████████ ███████ ███    ██ ██████   █████  ███    ██ ███████ ██      
██  ██  ██    ██       ██    ██      ████   ██ ██   ██ ██   ██ ████   ██ ██      ██      
█████   ██    ██       ██    █████   ██ ██  ██ ██████  ███████ ██ ██  ██ █████   ██      
██  ██  ██    ██       ██    ██      ██  ██ ██ ██      ██   ██ ██  ██ ██ ██      ██      
██   ██ ██    ██       ██    ███████ ██   ████ ██      ██   ██ ██   ████ ███████ ███████ 
Version - v{app.config['version']}

Copyright © 2021 MythicalKitten

 Source:  https://github.com/kittensaredabest/kittenpanel
License:  https://github.com/kittensaredabest/kittenpanel/blob/main/LICENSE

This software is made available under the terms of the MIT license.
The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
    """)
    args = ['uvicorn', 'server:app', '--host', str(config['webserver']['host']), '--port', str(config['webserver']['port']), '--workers', str(config['webserver']['workers'])]
    if config['webserver']['debug']:
        args.append('--reload')
    with open(os.devnull, 'w') as tempf:
        proc = subprocess.Popen(args, stdin=tempf)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Killing")
            try:
                proc.terminate()
                sys.exit(0)
            except OSError:
                pass
            proc.wait()
    #uvicorn.run("server:app", host=config['webserver']['host'], port=config['webserver']['port'], workers=config['webserver']['workers'])