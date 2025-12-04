import re
from typing import Optional, Type

from pydantic import BaseModel, ValidationError
from pymongo.collection import Collection


class Repository:
    """
    Generic repository using a Pydantic model to validate/serialize Mongo documents.
    """

    def __init__(self, collection: Collection, model_cls: Type[BaseModel]) -> None:
        self.collection = collection
        self.model_cls = model_cls

    def _serialize(self, doc: dict) -> Optional[dict]:
        payload = dict(doc)
        if "_id" in payload:
            payload["_id"] = str(payload["_id"])
        try:
            return self.model_cls.model_validate(payload).model_dump()
        except ValidationError:
            return None

    def insert_object_to_db(self, obj: BaseModel):
        self.collection.insert_one(obj.model_dump())

    def delete_all_objects_from_db(self):
        self.collection.delete_many({})

    def get_object_by_title(self, title: str) -> list[dict]:
        pattern = re.escape(title)
        cursor = self.collection.find({"title": {"$regex": pattern, "$options": "i"}})
        return [piece for doc in cursor if (piece := self._serialize(doc))]

    def get_object_by_style(self, style: str) -> list[dict]:
        variants = [style.lower(), style.capitalize(), style.upper()]
        cursor = self.collection.find({"style": {"$in": variants}})
        objects: list[dict] = []
        for doc in cursor:
            if (piece := self._serialize(doc)):
                objects.append(piece)
        return objects
