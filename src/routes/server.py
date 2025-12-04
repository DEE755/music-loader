
from main import app
import database
import asyncio
from pymongo import PyMongoError
from fastapi import HTTPException
from fastapi.responses import FileResponse

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    # Return DB status along with app status for simple monitoring
    if database.get_client() is None:
        return {"status": "ok", "db": "not_initialized"}

    try:
        await asyncio.to_thread(database.get_client().admin.command, "ping")
        db_status = "ok"
    except PyMongoError:
        db_status = "unhealthy"
    return {"status": "ok", "db": db_status}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")