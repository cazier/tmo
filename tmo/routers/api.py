from fastapi import APIRouter

from .bill import router as bill
from .subscriber import router as subscriber

api = APIRouter(prefix="/api", include_in_schema=True)

api.include_router(bill)
api.include_router(subscriber)

