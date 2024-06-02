import logging
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel, HttpUrl

from app.datamodel.attachment import AttachmentReference
from app.datamodel.dpp import DigitalProductPassport
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore
from app.datastores.data.basedatastore import BaseDataStore, DPPResponseContentFormats
from app.main import get_datastores

logger = logging.getLogger("dpp-api")


# Define a common response structure
class ErrorResponseModel(BaseModel):
    detail: str


# Define a success response example
class SuccessResponseModel(BaseModel):
    message: str


dpp_app = APIRouter(
    prefix="/dpps",
    tags=["Digital Product Passport"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
    responses={
        400: {"model": ErrorResponseModel, "description": "Bad Request"},
        404: {"model": ErrorResponseModel, "description": "Item Not Found"},
        500: {"model": ErrorResponseModel, "description": "Internal Server Error"},
    },
)


@dpp_app.get("/latest")
async def get_latest_dpp(datastores=Depends(get_datastores)):
    """
    UI-specific. Get the latest generated DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    latest_added_dpp_id = data_store.get_latest_added_dpp_document_id()
    return JSONResponse({"result": latest_added_dpp_id})


@dpp_app.get("/random")
async def get_random_dpp(datastores=Depends(get_datastores)):
    """
    UI-specific. Get a random DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    random_dpp_id = data_store.get_random_dpp_document_id()
    return JSONResponse({"result": random_dpp_id})


# Get a basic DPP without signature
@dpp_app.get("/{document_id}")
async def get_dpp_basic(document_id: str, datastores=Depends(get_datastores)):
    """
    Get basic DPP details without signature.
    """
    logger.debug("Retrieving DPP with ID -> " + document_id)
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    result = data_store.get_dpp_document(document_id)
    return JSONResponse(result)


@dpp_app.get("/{document_id}/full")
async def get_dpp_full(document_id: str, datastores=Depends(get_datastores)):
    """
    Get full DPP details including all attachments.
    """
    logger.debug("Retrieving full DPP with ID -> " + document_id)
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    result = data_store.get_dpp_document(
        document_id, content_format=DPPResponseContentFormats.FULL.value
    )
    return JSONResponse(result)


@dpp_app.post("/{document_id}/events/activity")
async def add_dpp_activity_event(
    document_id: str, event: Dict, datastores=Depends(get_datastores)
):
    """
    Add an activity event to a DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    data_store.add_dpp_event(document_id, event)
    return JSONResponse({"document_id": document_id, "event": event})


@dpp_app.post("/{document_id}/events/ownership")
async def add_dpp_ownership_event(
    document_id: str, event: Dict, datastores=Depends(get_datastores)
):
    """
    Add an ownership event to a DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    data_store.add_dpp_event(document_id, event, event_type="ownership")
    return JSONResponse({"document_id": document_id, "event": event})


@dpp_app.get("/{document_id}/events/activity")
async def get_dpp_activity_events(document_id: str, datastores=Depends(get_datastores)):
    """
    Get activity events of a DPP sorted.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    events = data_store.get_dpp_events(document_id)
    return JSONResponse(events)


@dpp_app.get("/{document_id}/events/ownership")
async def get_dpp_ownership_events(
    document_id: str, datastores=Depends(get_datastores)
):
    """
    Get ownership events of a DPP sorted.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    events = data_store.get_dpp_events(document_id, event_type="ownership")
    return JSONResponse(events)


@dpp_app.get("/{document_id}/events/activity/full")
async def get_dpp_full_activity_events(
    document_id: str, datastores=Depends(get_datastores)
):
    """
    Get complete activity events of a DPP sorted.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    events = data_store.get_dpp_full_events(document_id)
    return JSONResponse(events)


@dpp_app.get("/{document_id}/events/ownership/full")
async def get_dpp_full_ownership_events(
    document_id: str, datastores=Depends(get_datastores)
):
    """
    Get complete ownership events of a DPP sorted.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    events = data_store.get_dpp_full_events(document_id, event_type="ownership")
    return JSONResponse(events)


# WIP: Attachment endpoints
# If possible to add some documentation regarding instances, something
# like Minio should be deployed along-side to handle file-storage.
# @dpp_app.get("/{uuid}/attachments/{attachment_id}")
# async def add_dpp_attachment(uuid: UUID4, attachments: FileAttachment):
#     return FileResponse()


@dpp_app.get("/{document_id}/attachments/{attachment_id}")
async def get_dpp_attachment(
    document_id: str, attachment_id: str, datastores=Depends(get_datastores)
):
    attachment_store: BaseAttachmentStore = datastores[1]
    return attachment_store.retrieve_attachment(attachment_id)


@dpp_app.get("/{document_id}/attachments/{attachment_id}/thumbnail")
async def get_dpp_attachment_thumbnail(
    document_id: str, attachment_id: str, datastores=Depends(get_datastores)
):
    attachment_store: BaseAttachmentStore = datastores[1]
    return attachment_store.retrieve_attachment_thumbnail(attachment_id, (None, 100))


@dpp_app.get("/{document_id}/attachments")
async def get_dpp_attachments(
    document_id: str,
    datastores=Depends(get_datastores),
):
    """
    Add attachments to a DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    dpp: DigitalProductPassport = data_store.get_dpp_object(document_id)
    attachment_references = [
        attachment_store.attachments_index[id].to_public_dict()
        for id in dpp.attachments
    ]
    # Your implementation here
    return JSONResponse(attachment_references)


@dpp_app.post("/{document_id}/attachments")
async def add_dpp_attachment(
    document_id: str,
    file: UploadFile = File(...),
    attachment_type: str = Form(...),
    source: str = Form("instance"),
    template_id: Optional[str] = Form(None),
    template_version: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_default: Optional[bool] = Form(None),
    datastores=Depends(get_datastores),
):
    """
    Add attachments to a DPP.
    """
    data_store: BaseDataStore = datastores[0]
    attachment_store: BaseAttachmentStore = datastores[1]
    partial_attachment_reference = AttachmentReference(
        attachment_type=attachment_type,  # type: ignore
        path=None,
        source=source,  # type: ignore
        template_id=template_id,
        template_version=template_version,
        description=description,
        is_default=is_default,
    )
    completed_attachment_reference = attachment_store.add_attachment(
        file, attachment_reference=partial_attachment_reference
    )
    # Your implementation here
    return JSONResponse(completed_attachment_reference.to_public_dict())


@dpp_app.put("/{uuid}/attachments/{attachment_id}")
async def update_attachment(
    uuid: UUID4,
    attachment_id: UUID4,
    # attachment: UpdateFileAttachmentModel
):
    """
    Update a file attachment for a DPP instance
    """
    raise HTTPException(status_code=500, detail="Not implemented!")
    # return {
    #     "uuid": uuid,
    #     "attachment_id": attachment_id,
    #     "updated_attachment": attachment,
    # }


@dpp_app.delete("/{uuid}/attachments/{attachment_id}")
async def delete_attachment(uuid: UUID4, attachment_id: UUID4):
    """
    Delete a file attachment from a DPP instance
    """
    raise HTTPException(status_code=500, detail="Not implemented!")
    # return {"uuid": uuid, "attachment_id": attachment_id, "deleted": True}


# Instantiate a DPP from a template
@dpp_app.post(
    "/{template_id_short}",
)
async def create_dpp(
    template_id_short: str,
    version: str = Query("latest"),
    # attributes: CreateDPPRequest = Body(...),
    datastores=Depends(get_datastores),
):
    """
    Create a DPP from a template with specified version.
    """
    # Business logic to create a DPP from the template
    # return {
    #     "message": "DPP created",
    #     "template_id_short": template_id_short,
    #     "version": version,
    #     "attributes": attributes,
    # }
    raise HTTPException(500, "Not implemented!")


# Alternate endpoint to do the same as above.
@dpp_app.post("/dpp-templates/{id_short}/create")
async def create_dpp_from_template(
    id_short: str,
    version: Optional[str] = Query(None),
    # attributes: CreateDPPRequest = Body(...),
    datastores=Depends(get_datastores),
):
    """
    Alternative method to create a DPP from a template.
    """
    # Similar business logic to create a DPP from the template
    # return {
    #     "message": "DPP created from template",
    #     "id_short": id_short,
    #     "version": version,
    #     "attributes": attributes,
    # }
    raise HTTPException(500, "Not implemented!")


@dpp_app.get("/{uuid}/self-signed")
async def get_dpp_self_signed(uuid: UUID4):
    """
    Get basic DPP details with self-signature.
    """
    # return {"uuid": uuid, "detail": "Basic DPP details with self-signature"}
    raise HTTPException(500, "Not implemented!")


@dpp_app.get("/{uuid}/signed")
async def get_dpp_signed(uuid: UUID4):
    """
    Get DPP details with embedded signatures/presentations from third parties.
    """
    # return {"uuid": uuid, "detail": "DPP details with embedded signatures"}
    raise HTTPException(500, "Not implemented!")


# Add event data to a DPP. If it is not clear what is
# being added, it will go straight to event-log.
@dpp_app.post("/{document_id}/events")
async def add_dpp_event(document_id: str, event: Dict):
    """
    Add an event to a DPP.
    """
    # return {"document_id": document_id, "event": event}
    raise HTTPException(500, "Not implemented!")
