from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

import src.config as config
from src.DI.container import get_piece_dao
from src.scrapping import mutopia


router = APIRouter()
piece_dao= get_piece_dao()


@router.get("/pieces/styles/{style}")
async def get_pieces_by_style(style: str) -> list[dict]:
    try:
        pieces = piece_dao.get_pieces_by_style(style)
        return [piece for piece in pieces]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/start-scrapping")
async def start_scrapping_endpoint():
    print("Starting scrapping...")
    mutopia.start_scrapping(max_pieces=config.MAX_PIECES, delay=config.SCRAPPING_DELAY)
    return {"status": "started"}


@router.get("/pieces/title/{title}")
async def get_pieces_by_name(title: str) -> list[dict]:
    try:
        pieces = piece_dao.get_pieces_by_title(title)
        return [piece for piece in pieces]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
