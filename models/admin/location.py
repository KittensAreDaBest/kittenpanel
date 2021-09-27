from pydantic import BaseModel

class Location(BaseModel):
    name: str
    pterodactyl: int
    allowed_eggs: list
    allowed_plans: list

