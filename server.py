from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import RedirectResponse
import uvicorn
import git
import aiohttp
from routes import api_admin, api_client, oauth, dashboard, default
from utils import mongodb
from dependencies import AuthenticationException
with open("config.json", "rb") as file:
    config = json.load(file)

app = FastAPI(title=config['appname'], docs_url="/api/docs", redoc_url="/api/docs")
app.config = config

app.mount("/static", StaticFiles(directory="static"), name="static")

app.database = mongodb.MongoDB(config['database'])
app.session = aiohttp.ClientSession()

app.add_event_handler("startup", app.database.connect_db)
app.add_event_handler("shutdown", app.database.close_db)
app.templates = Jinja2Templates(directory="templates")

@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
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
Version - {git.Repo(search_parent_directories=True).git.rev_parse("HEAD", short=7)}

Copyright © 2021 MythicalKitten

 Source:  https://github.com/kittensaredabest/kittenpanel
License:  https://github.com/kittensaredabest/kittenpanel/blob/main/LICENSE

This software is made available under the terms of the MIT license.
The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
    """)
    uvicorn.run("server:app", host=config['webserver']['host'], port=config['webserver']['port'], reload=config['webserver']['debug'], debug=config['webserver']['debug'], workers=config['webserver']['workers'])