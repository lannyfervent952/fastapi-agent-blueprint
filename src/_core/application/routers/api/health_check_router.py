from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src._core.infrastructure.database.database import Database
from src._core.infrastructure.di.core_container import CoreContainer

router = APIRouter()


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@router.get("/health/db")
@inject
async def database_health_check(
    database: Database = Depends(Provide[CoreContainer.database]),
):
    try:
        async with database.session() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "healthy"}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "detail": str(e)},
            status_code=503,
        )
