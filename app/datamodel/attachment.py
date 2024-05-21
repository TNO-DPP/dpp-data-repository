from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


class AttachmentType(Enum):
    DOCUMENT = "document"
    IMAGE = "image"


class AttachmentSourceType(Enum):
    TEMPLATE = "template"
    INSTANCE = "instance"


@dataclass
class AttachmentReference:
    attachment_type: AttachmentType
    # Filepath for Filesystem, s3 path for s3 stores. # Not provided in public reference.
    path: Optional[str]
    source: AttachmentSourceType

    # One of source_id or template_id must be present, but both can be present together.
    source_id: Optional[str] = None  # UUID for DPP
    template_id: Optional[str] = None  # ShortID for Templates.
    # Could be retrieving something from an older template version
    template_version: Optional[str] = None

    link: Optional[str] = None  # Maybe generated link, for ease of UI.
    description: Optional[str] = None
    is_default: Optional[bool] = False
    attachment_id: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def to_public_dict(self):
        output = {
            "type": self.attachment_type,
            "source": self.source,
            "attachment_id": self.attachment_id,
            "description": self.description,
            "file_name": self.file_name,
            "file_size": self.file_size,
        }
        if self.source == AttachmentSourceType.TEMPLATE.value:
            output["template_id"] = self.template_id
            output["template_version"] = self.template_version
        if self.source_id:
            output["source_id"] = self.source_id
        return output
