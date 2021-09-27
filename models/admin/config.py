from pydantic import BaseModel
from typing import Optional

class ShopConfig(BaseModel):
    shop_cpu: bool
    shop_cpu_price: Optional[int] = None
    shop_cpu_min: Optional[int] = None
    
    shop_ram: bool
    shop_ram_price: Optional[int] = None
    shop_ram_min: Optional[int] = None

    shop_hdd: bool
    shop_hdd_price: Optional[int] = None
    shop_hdd_min: Optional[int] = None

    shop_backups: bool
    shop_backups_price: Optional[int] = None

    shop_port: bool
    shop_port_price: Optional[int] = None

    shop_database: bool
    shop_database_price: Optional[int] = None

    shop_slots: bool
    shop_slots_price: Optional[int] = None

    promo_code: bool

class ServerConfig(BaseModel):
    server_creation: bool
    server_deletion: bool
    server_editing: bool

class UserConfig(BaseModel):
    user_creation: bool
