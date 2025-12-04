from fastapi import logger
from pydantic import BaseModel, Field, field_validator


class MusicalPiece(BaseModel):
    title: str
    composer: str | None = None
    instruments: str | None = None
    style: str | None = None
    opus: str | None = None
    date_of_composition: str | None = None
    source: str | None = None
    copyright: str | None = None
    last_updated: str | None = None
    music_id_number: str | None = None
    pdf_url: str | None = None
    format: str | None = None
    db_id: str | None = Field(default=None, alias="_id")

    @field_validator("title")
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title must not be empty")
        return v
    
    @field_validator("pdf_url")
    def pdf_url_must_not_be_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("PDF URL must not be empty if provided")
        return v

    model_config = {"populate_by_name": True}
    
    def _serialize_document(self,doc: dict) -> dict | None:
        """
        Validate and serialize a Mongo document into a JSON-serializable dict
        using the MusicalPiece Pydantic model.
        """
        payload = dict(doc)
        if "_id" in payload:
            payload["_id"] = str(payload["_id"])

        try:
            piece = self.model_validate(payload)
            return piece.model_dump()
        except self.ValidationError as exc:
            logger.warning("Skipping invalid document %s: %s", doc.get("_id"), exc)
            return None

    
    
