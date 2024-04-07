from typing import List, Optional

from pydantic import UUID4, BaseModel, HttpUrl


class Attribute(BaseModel):
    name: str
    value: Optional[str] = None


class Event(BaseModel):
    type: str
    content: dict


class CreateDPPRequest(BaseModel):
    attributes: List[Attribute]


class EventAddRequest(BaseModel):
    event_type: str
    details: dict


class FileAttachment(BaseModel):
    file_url: HttpUrl


class FileAttachmentModel(BaseModel):
    file_name: str
    file_url: HttpUrl


class UpdateFileAttachmentModel(BaseModel):
    file_name: Optional[str]
    file_url: Optional[HttpUrl]
