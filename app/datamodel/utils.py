# Contains definitions for DPP templates, JSON Schema, Versions,
# - all aspects supporting the backend application.
# ACL models be in a sibling file.
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


# Models
class AttributeModel(BaseModel):
    name: str
    data_type: str
    description: Optional[str] = None


class EventModel(BaseModel):
    event_name: str
    event_description: Optional[str] = None


class CredentialModel(BaseModel):
    credential_name: str
    credential_schema_url: HttpUrl


class FileAttachment(BaseModel):
    file_url: HttpUrl


class FileAttachmentModel(BaseModel):
    file_name: str
    file_url: HttpUrl


class UpdateAttributeModel(BaseModel):
    name: Optional[str]
    data_type: Optional[str]
    description: Optional[str]


class UpdateEventModel(BaseModel):
    event_name: Optional[str]
    event_description: Optional[str]


class UpdateCredentialModel(BaseModel):
    credential_name: Optional[str]
    credential_schema_url: Optional[HttpUrl]


class UpdateFileAttachmentModel(BaseModel):
    file_name: Optional[str]
    file_url: Optional[HttpUrl]


class TemplatePublishVersion(str, Enum):
    latest = "latest"
    specific_version = (
        "specific_version"  # This is a placeholder, implement version logic as needed.
    )
