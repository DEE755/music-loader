from src.schemas.models import MusicalPiece
from src.database.database import Database
from src.database.db_repository import Repository


class MusicalPieceDAO:
    """
    DAO for MusicalPiece documents, backed by the shared Database instance.
    """

    def __init__(self, db: Database):
        self.db = db
        self.repository = Repository(collection=db.pieces_collection, model_cls=MusicalPiece)

    def insert_object_to_db(self, piece: MusicalPiece):
        self.repository.insert_object_to_db(piece)

    def get_pieces_by_title(self, title: str) -> list[dict]:
        return self.repository.get_object_by_title(title)

    def get_pieces_by_style(self, style: str) -> list[dict]:
        return self.repository.get_object_by_style(style)
