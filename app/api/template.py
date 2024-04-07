# Contains API endpoints for DPP Templates, and all associated contents.
#
from fastapi import Body, FastAPI, HTTPException, Path, Query
from pydantic import UUID4

from ..datamodel.utils import *
from ..main import app


# Initially create a shell for DPP templates, optionally with some content auto-added.
@app.post("/dpp-templates/")
async def create_dpp_template(template_body: dict = Body(...)):
    """
    Create DPP Template
    """
    return {"template_id": "UUID", "template_body": template_body}


# Attribute endpoints to DPP templates
@app.post("/dpp-templates/{uuid}/attributes")
async def add_attributes(uuid: UUID4, attributes: AttributeModel):
    """
    Add attributes to a DPP template.
    """
    # Your implementation here
    return {"uuid": uuid, "added_attributes": attributes}


@app.delete("/dpp-templates/{template_id}/attributes/{attribute_id}")
async def delete_attribute(template_id: UUID4, attribute_id: UUID4):
    """
    Delete an attribute from a DPP template
    """
    return {"template_id": template_id, "attribute_id": attribute_id, "deleted": True}


# Event endpoints for DPP templates
@app.post("/dpp-templates/{uuid}/events")
async def add_events(uuid: UUID4, events: EventModel):
    """
    Add event models to a DPP template.
    """
    # Your implementation here
    return {"uuid": uuid, "added_events": events}


@app.put("/dpp-templates/{template_id}/events/{event_id}")
async def update_event(template_id: UUID4, event_id: UUID4, event: UpdateEventModel):
    """
    Update an event model for a DPP template
    """
    return {"template_id": template_id, "event_id": event_id, "updated_event": event}


@app.delete("/dpp-templates/{template_id}/events/{event_id}")
async def delete_event(template_id: UUID4, event_id: UUID4):
    """
    Delete an event model from a DPP template
    """
    return {"template_id": template_id, "event_id": event_id, "deleted": True}


# WIP: Credential endpoints for DPP templates
# These credentials are either embedded documents with some information
# regarding the actual credential stored in an external SSI wallet.
@app.post("/dpp-templates/{uuid}/credentials")
async def add_credentials(uuid: UUID4, credentials: CredentialModel):
    """
    Add credentials to a DPP template.
    """
    # Your implementation here
    return {"uuid": uuid, "added_credentials": credentials}


@app.put("/dpp-templates/{template_id}/credentials/{credential_id}")
async def update_credential(
    template_id: UUID4, credential_id: UUID4, credential: UpdateCredentialModel
):
    """
    Update a credential model for a DPP template
    """
    return {
        "template_id": template_id,
        "credential_id": credential_id,
        "updated_credential": credential,
    }


@app.delete("/dpp-templates/{template_id}/credentials/{credential_id}")
async def delete_credential(template_id: UUID4, credential_id: UUID4):
    """
    Delete a credential model from a DPP template
    """
    return {"template_id": template_id, "credential_id": credential_id, "deleted": True}


# WIP: Attachment endpoints
# If possible to add some documentation regarding a template or to instances, something
# like Minio should be deployed along-side to handle file-storage.
@app.post("/dpp-templates/{uuid}/attachments")
async def add_attachments(uuid: UUID4, attachments: FileAttachment):
    """
    Attach files to a DPP template.
    """
    # Your implementation here
    return {"uuid": uuid, "added_attachments": attachments}


@app.put("/dpp-templates/{template_id}/attachments/{attachment_id}")
async def update_attachment(
    template_id: UUID4, attachment_id: UUID4, attachment: UpdateFileAttachmentModel
):
    """
    Update a file attachment for a DPP template
    """
    return {
        "template_id": template_id,
        "attachment_id": attachment_id,
        "updated_attachment": attachment,
    }


@app.delete("/dpp-templates/{template_id}/attachments/{attachment_id}")
async def delete_attachment(template_id: UUID4, attachment_id: UUID4):
    """
    Delete a file attachment from a DPP template
    """
    return {"template_id": template_id, "attachment_id": attachment_id, "deleted": True}


# Versioning and Publishing of templates to enable replicability, stability.
# (potentially documentation of a diff and a migration path, if possible.)
@app.post("/dpp-templates/{uuid}/publish/{version}")
async def publish_template(uuid: UUID4, version: TemplatePublishVersion):
    """
    Lock and publish a specific version of a DPP template.
    """
    # Implement template versioning and publishing logic here
    return {"uuid": uuid, "published_version": version}


@app.put("/dpp-templates/{template_id}/version/{version}")
async def update_template_version(
    template_id: UUID4, version: str, template_body: dict = Body(...)
):
    """
    Update version content of a DPP template
    """
    return {
        "template_id": template_id,
        "version": version,
        "updated_content": template_body,
    }


@app.delete("/dpp-templates/{template_id}/version/{version}")
async def delete_template_version(template_id: UUID4, version: str):
    """
    Delete a version of a DPP template
    """
    return {"template_id": template_id, "version": version, "deleted": True}


# WIP: ACL configuration based on current attributes.
# Multiple strategies exist to support this, and none have been picked over the other.
@app.post("/dpp-templates/{uuid}/acls")
async def set_acls(uuid: UUID4, acl_settings: dict = Body(...)):
    """
    Set Access Control Lists for a specific DPP template.
    """
    # Your ACL implementation here
    return {"uuid": uuid, "acl_settings": acl_settings}
