import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional

from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.datamodel.attachment import AttachmentReference

ID_ALPHABET = string.ascii_lowercase + string.digits


# @dataclass
# class AttachmentStoreStatistics:
#     dpp_attachments: int = 0
#     dpp_template_attachments: int = 0


class BaseAttachmentStore(ABC):
    # Importantly, no single link exists for accessing files, except what is available through the link behind an attachment.
    # Core functionalities
    # - Have some configuration to connect to store/validate availability
    # - Have a structure of referencing attachments (unique-id function is provided in base.)
    #   - This is provided as attachment reference in the API. It returns the right file link.
    # An example structure for the FileSystemAttachmentStore
    # -> self.attachments = []
    # -> self.attachments[unique_id] = AttachmentReference
    # - unique ID - connected to Instance, or Template
    # - Update and Remove the same. If connected to a DPP, trigger a Delta event.
    # - Some resizing of image content, based on requirement.
    def __init__(self) -> None:
        super().__init__()
        self.attachments_index: Dict[str, AttachmentReference] = {}

    @staticmethod
    def generate_unique_id_for_uploaded_attachment():
        return "".join(random.choices(ID_ALPHABET, k=8))

    # No path, attachment reference will be
    @abstractmethod
    def add_attachment(
        self, file: UploadFile, attachment_reference: AttachmentReference
    ) -> AttachmentReference:
        pass

    @abstractmethod
    def retrieve_attachment(self, attachment_id: str) -> FileResponse:
        pass

    # For specific images that may need backend reshaping
    @abstractmethod
    def retrieve_attachment_thumbnail(self, attachment_id: str) -> FileResponse:
        pass

    # Receive attachment ID, replace attachment that already existed.
    @abstractmethod
    def update_attachment(
        self, file: UploadFile, attachment_id: str
    ) -> AttachmentReference:
        pass

    @abstractmethod
    def delete_attachment(self, attachment_id: str):
        pass
