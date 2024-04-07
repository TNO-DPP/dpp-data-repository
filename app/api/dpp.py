from typing import List, Optional

from fastapi import Body, FastAPI, Path, Query
from pydantic import UUID4, BaseModel, HttpUrl

from ..datamodel.dpp import *
from ..main import app


# Instantiate a DPP from a template
@app.post("/dpps/{template_id_short}")
async def create_dpp(
    template_id_short: str,
    version: str = Query("latest"),
    attributes: CreateDPPRequest = Body(...),
):
    """
    Create a DPP from a template with specified version.
    """
    # Business logic to create a DPP from the template
    return {
        "message": "DPP created",
        "template_id_short": template_id_short,
        "version": version,
        "attributes": attributes,
    }


# Alternate endpoint to do the same as above.
@app.post("/dpp-templates/{id_short}/create")
async def create_dpp_from_template(
    id_short: str,
    version: Optional[str] = Query(None),
    attributes: CreateDPPRequest = Body(...),
):
    """
    Alternative method to create a DPP from a template.
    """
    # Similar business logic to create a DPP from the template
    return {
        "message": "DPP created from template",
        "id_short": id_short,
        "version": version,
        "attributes": attributes,
    }


# Get a basic DPP without signature
@app.get("/dpps/{uuid}")
async def get_dpp_basic(uuid: UUID4):
    """
    Get basic DPP details without signature.
    """
    return {"uuid": uuid, "detail": "Basic DPP details"}


@app.get("/dpps/{uuid}/self-signed")
async def get_dpp_self_signed(uuid: UUID4):
    """
    Get basic DPP details with self-signature.
    """
    return {"uuid": uuid, "detail": "Basic DPP details with self-signature"}


@app.get("/dpps/{uuid}/signed")
async def get_dpp_signed(uuid: UUID4):
    """
    Get DPP details with embedded signatures/presentations from third parties.
    """
    return {"uuid": uuid, "detail": "DPP details with embedded signatures"}


@app.get("/dpps/{uuid}/full")
async def get_dpp_full(uuid: UUID4):
    """
    Get full DPP details including all attachments.
    """
    return {"uuid": uuid, "detail": "Full DPP details with attachments"}


@app.get("/dpps/latest")
async def get_latest_dpp():
    """
    UI-specific. Get the latest generated DPP.
    """
    return {"detail": "Latest DPP data"}


@app.get("/dpps/random")
async def get_random_dpp():
    """
    UI-specific. Get a random DPP.
    """
    return {"detail": "Random DPP data"}


# Add event data to a DPP. If it is not clear what is
# being added, it will go straight to event-log.
@app.post("/dpps/{uuid}/events")
async def add_dpp_event(uuid: UUID4, event: Event):
    """
    Add an event to a DPP.
    """
    return {"uuid": uuid, "event": event}


@app.post("/dpps/{uuid}/events/activity")
async def add_dpp_activity_event(uuid: UUID4, activity_event: EventAddRequest):
    """
    Add an activity event to a DPP.
    """
    return {"uuid": uuid, "activity_event": activity_event}


@app.post("/dpps/{uuid}/events/ownership")
async def add_dpp_ownership_event(uuid: UUID4, ownership_event: EventAddRequest):
    """
    Add an ownership event to a DPP.
    """
    return {"uuid": uuid, "ownership_event": ownership_event}


@app.get("/dpps/{uuid}/events/activity")
async def get_dpp_activity_events(uuid: UUID4):
    """
    Get activity events of a DPP.
    """
    return {"uuid": uuid, "events": "Activity events"}


@app.get("/dpps/{uuid}/events/ownership")
async def get_dpp_ownership_events(uuid: UUID4):
    """
    Get ownership events of a DPP.
    """
    return {"uuid": uuid, "events": "Ownership events"}


# WIP: Attachment endpoints
# If possible to add some documentation regarding instances, something
# like Minio should be deployed along-side to handle file-storage.
@app.post("/dpps/{uuid}/attachments")
async def add_dpp_attachment(uuid: UUID4, attachments: FileAttachment):
    """
    Add attachments to a DPP.
    """
    # Your implementation here
    return {"uuid": uuid, "added_attachments": attachments}


@app.put("/dpps/{uuid}/attachments/{attachment_id}")
async def update_attachment(
    uuid: UUID4, attachment_id: UUID4, attachment: UpdateFileAttachmentModel
):
    """
    Update a file attachment for a DPP instance
    """
    return {
        "uuid": uuid,
        "attachment_id": attachment_id,
        "updated_attachment": attachment,
    }


@app.delete("/dpps/{uuid}/attachments/{attachment_id}")
async def delete_attachment(uuid: UUID4, attachment_id: UUID4):
    """
    Delete a file attachment from a DPP instance
    """
    return {"uuid": uuid, "attachment_id": attachment_id, "deleted": True}
