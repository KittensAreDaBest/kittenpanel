from fastapi import APIRouter
from starlette.requests import Request
router = APIRouter(prefix="/dashboard")

@router.get("/")
async def get_dashboard(request: Request):
    return {"test": "test1234"}