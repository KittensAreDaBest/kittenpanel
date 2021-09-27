from pydantic import BaseModel
from typing import Optional

class Codes(BaseModel):
    id: str
    cpu: Optional[int] = None
    ram: Optional[int] = None
    hdd: Optional[int] = None
    backups: Optional[int] = None
    ports: Optional[int] = None
    databases: Optional[int] = None

