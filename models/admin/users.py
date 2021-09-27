from pydantic import BaseModel

class User(BaseModel):
    id: int
    pterodactyl: int
    plan: int
    disabled: bool
    cpu: int
    ram: int
    disk: int
    servers: int
    backups: int
    ports: int
    databases: int