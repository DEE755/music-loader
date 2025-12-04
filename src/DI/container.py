from functools import lru_cache

from src.database.database import Database
from src.database.musical_piece_dao import MusicalPieceDAO


class Container:
    def __init__(self) -> None:
        self.db = Database()
        self.piece_dao = MusicalPieceDAO(db=self.db)


@lru_cache
def get_container() -> Container:
    return Container()


def get_db() -> Database:
    return get_container().db


def get_piece_dao() -> MusicalPieceDAO:
    return get_container().piece_dao
