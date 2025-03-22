import fastapi

from .bill import router as bill
from .charge import router as charge
from .detail import router as detail
from .shared import router as shared
from .subscriber import router as subscriber

api = fastapi.APIRouter(prefix="/api", include_in_schema=True)

api.include_router(bill)
api.include_router(charge)
api.include_router(detail)
api.include_router(shared)
api.include_router(subscriber)
