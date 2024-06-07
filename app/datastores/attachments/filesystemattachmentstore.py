import io
import json
import logging
import os
import random
import shutil
import string
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image

from app.config import format_multiline_log
from app.datamodel.attachment import AttachmentReference, AttachmentSourceType
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore

logger = logging.getLogger("fs-file-store")


class FileSystemAttachmentStore(BaseAttachmentStore):
    def __init__(self, attachment_config, reset=False) -> None:
        super().__init__()
        self.FILE_DIRECTORY = Path(os.path.join(os.getcwd(), attachment_config["path"]))
        if reset:
            if os.path.exists(self.FILE_DIRECTORY):
                logger.debug("Found existing data, permanently deleting existing data.")
                shutil.rmtree(self.FILE_DIRECTORY)
        self.FILE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        self.DPP_FILE_DIRECTORY = Path(os.path.join(self.FILE_DIRECTORY, "dpps"))
        self.DPP_FILE_DIRECTORY.mkdir(exist_ok=True)
        self.DPP_TEMPLATES_FILE_DIRECTORY = Path(
            os.path.join(self.FILE_DIRECTORY, "templates")
        )
        self.DPP_TEMPLATES_FILE_DIRECTORY.mkdir(exist_ok=True)

    def generate_path(self, partial_attachment_ref: AttachmentReference):
        if partial_attachment_ref.source == AttachmentSourceType.INSTANCE:
            assert partial_attachment_ref.source_id is not None
            file_path = os.path.join(
                self.DPP_FILE_DIRECTORY, partial_attachment_ref.source_id
            )
            return file_path
        elif partial_attachment_ref.source == AttachmentSourceType.TEMPLATE:
            # Published versions are intended to be immutable.
            version = "vLatest"
            assert partial_attachment_ref.template_id is not None
            file_path = os.path.join(
                self.DPP_FILE_DIRECTORY,
                os.path.join(version, partial_attachment_ref.template_id),
            )
            return file_path
        else:
            raise Exception("Unable to create path to store file.")

    # Partial AttachmentReference is created at the API endpoint side, where it contains
    # - attachment_type : "image/document" for now
    # - source - "instance/template" for now, template defaults to "vLatest", published versions
    #           are made immutable
    # - source_id - "uuid/idshort" based on what the above was
    # - description - if provided
    # - is_default - if image, and if provided.

    def add_attachment(
        self, file: UploadFile, partial_attachment_ref: AttachmentReference
    ) -> AttachmentReference:
        unique_file_id = self.generate_unique_id_for_uploaded_attachment()

        file_path = Path(self.generate_path(partial_attachment_ref))

        try:
            # Ensure the directory exists
            file_path.mkdir(parents=True, exist_ok=True)

            # Save the file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Populate and return the AttachmentReference
            completed_attachment_reference = AttachmentReference(
                # Assuming you have a way to determine or receive this
                attachment_type=partial_attachment_ref.attachment_type,
                path=file_path.as_posix(),
                source=partial_attachment_ref.source,
                source_id=partial_attachment_ref.source_id,
                template_id=partial_attachment_ref.template_id,
                template_version=partial_attachment_ref.template_version,
                description=partial_attachment_ref.description,
                is_default=partial_attachment_ref.is_default,
                attachment_id=unique_file_id,
                file_size=file.size,
                file_name=file.filename,
            )
            self.attachments_index[unique_file_id] = completed_attachment_reference
            return completed_attachment_reference
        except:
            raise Exception("Error uploading attachment.")
        finally:
            file.file.close()

    # Special function only for filesystemattachmentstore.
    # Receives a partial manifest with some data, and recreates paths
    # by running through index and identifying files.
    # Assumes that the files are present.
    def import_attachments(self, attachment_manifest: Dict) -> None:
        for attachment_id in attachment_manifest.keys():
            attachment_information = attachment_manifest[attachment_id]

            if attachment_information["source"] == AttachmentSourceType.INSTANCE.value:
                container_id = attachment_information["source_id"]
                path = os.path.join(
                    self.DPP_FILE_DIRECTORY,
                    attachment_information["source_id"],
                    attachment_information["file_name"],
                )
            else:
                container_id = attachment_information["template_id"]
                path = os.path.join(
                    self.DPP_TEMPLATES_FILE_DIRECTORY,
                    attachment_information["template_id"],
                    attachment_information["template_version"],
                    attachment_information["file_name"],
                )
            if not os.path.isfile(path):
                logger.error(
                    "Unable to find "
                    + attachment_id
                    + " -> "
                    + attachment_information["file_name"]
                    + " at "
                    + path
                )
                logger.error(" for " + container_id)
            else:

                completed_attachment_reference = AttachmentReference(
                    attachment_type=attachment_information["type"],
                    path=Path(path).as_posix(),
                    source=attachment_information["source"],
                    source_id=(attachment_information.get("source_id", None)),
                    template_id=(attachment_information.get("template_id", None)),
                    template_version=(
                        attachment_information.get("template_version", None)
                    ),
                    description=(
                        attachment_information.get("description", "Default description")
                    ),
                    is_default=(attachment_information.get("is_default", None)),
                    attachment_id=attachment_id,
                    file_name=attachment_information["file_name"],
                    file_size=os.path.getsize(path),
                )
                # Add to dict
                self.attachments_index[attachment_id] = completed_attachment_reference

        logger.info(
            "Imported " + str(len(self.attachments_index.keys())) + " attachments!"
        )
        # logger.info(
        #     format_multiline_log(
        #         json.dumps(
        #             {k: v.to_dict() for k, v in self.attachments_index.items()},
        #             indent=2,
        #         )
        #     )
        # )

    def retrieve_attachment(self, attachment_id: str) -> FileResponse:
        # First check if it exists in attachment index
        if attachment_id not in self.attachments_index:
            raise FileNotFoundError("Attachment missing.")
        else:
            attachment_reference = self.attachments_index[attachment_id]
            file_path = attachment_reference.path
            if file_path is None:
                raise FileNotFoundError("Attachment found, but not available in store.")
            return FileResponse(file_path, filename=attachment_reference.file_name)

    # def retrieve_attachment_thumbnail(self, attachment_id: str, dimensions: Tuple[int, int]) -> FileResponse:
    #     # First check if it exists in attachment index
    #     if attachment_id not in self.attachments_index:
    #         raise FileNotFoundError("Attachment missing.")

    #     raise NotImplementedError
    def retrieve_attachment_thumbnail(
        self,
        attachment_id: str,
        dimensions: Tuple[Optional[int], Optional[int]] = (None, None),
    ) -> FileResponse:
        # First check if it exists in attachment index
        if attachment_id not in self.attachments_index:
            raise FileNotFoundError("Attachment missing.")

        attachment_reference = self.attachments_index[attachment_id]
        file_path = attachment_reference.path
        if file_path is None:
            raise FileNotFoundError("Attachment found, but not available in store.")

        try:
            with Image.open(file_path) as img:
                original_width, original_height = img.size

                # Extract dimensions
                width, height = dimensions

                # Calculate new dimensions maintaining aspect ratio
                if width is None and height is None:
                    # If no dimensions are provided, return the original image
                    width, height = original_width, original_height
                elif width is None and height is not None:
                    # Scale based on the provided height
                    aspect_ratio = original_width / original_height
                    width = int(height * aspect_ratio)
                elif height is None and width is not None:
                    # Scale based on the provided width
                    aspect_ratio = original_height / original_width
                    height = int(width * aspect_ratio)
                else:
                    # Scale based on both provided dimensions, maintaining aspect ratio
                    img.thumbnail((width, height))
                    width, height = img.size

                img = img.resize((width, height), Image.Resampling.LANCZOS)

                # Determine the format from the original image
                image_format = img.format or "jpeg"

                # Convert RGBA to RGB if saving as JPEG
                if image_format.lower() == "jpeg" and img.mode == "RGBA":
                    img = img.convert("RGB")

                # Save the resized image to a temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{image_format.lower()}"
                ) as tmp:
                    img.save(tmp, format=image_format)
                    tmp_path = tmp.name

                media_type = f"image/{image_format.lower()}"
                return FileResponse(
                    tmp_path,
                    media_type=media_type,
                    filename=f"thumbnail_{attachment_reference.file_name}",
                )

        except Exception as e:
            raise Exception(f"Error generating thumbnail: {e}")

    def update_attachment(
        self, file: UploadFile, attachment_id: str
    ) -> AttachmentReference:
        # First check if it exists in attachment index
        if attachment_id not in self.attachments_index:
            raise FileNotFoundError("Attachment missing.")

        attachment_reference = self.attachments_index[attachment_id]
        if attachment_reference.path is None:
            raise FileNotFoundError("Attachment found, but not available in store.")
        file_path = Path(attachment_reference.path)

        try:
            # Save the new file, replacing the old one
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Update metadata if needed
            attachment_reference.file_size = file.size
            attachment_reference.file_name = file.filename

            # Return the updated attachment reference
            return attachment_reference
        except Exception as e:
            raise Exception(f"Error updating attachment: {e}")
        finally:
            file.file.close()

    def delete_attachment(self, attachment_id: str):
        # First check if it exists in attachment index
        if attachment_id not in self.attachments_index:
            raise FileNotFoundError("Attachment missing.")
        else:
            attachment_reference = self.attachments_index.pop(attachment_id)
            if attachment_reference.path is None:
                raise FileNotFoundError("Attachment found, but not available in store.")
            file_path = Path(attachment_reference.path)
            file_path.unlink(missing_ok=True)
            return {"status": "deleted"}
