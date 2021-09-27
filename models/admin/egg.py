from pydantic import BaseModel
from typing import Optional

class Egg(BaseModel):
    name: str
    nest: int
    egg: int
    docker: str
    docker_image: Optional[str] = None
    startup_command: Optional[str] = None
    variables: Optional[dict] = None
