from pydantic import BaseModel

class Plan(BaseModel):
    name: str
    default: bool
    cpu: int
    ram: int
    disk: int
    servers: int
    backups: int
    ports: int
    databases: int