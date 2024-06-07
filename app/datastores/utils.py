import json
import logging
import os
import shutil
from typing import Dict

from app.config import config
from app.datamodel.serde import import_dpp_into_storage
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore
from app.datastores.attachments.filesystemattachmentstore import (
    FileSystemAttachmentStore,
)
from app.datastores.data.basedatastore import BaseDataStore
from app.datastores.data.inmemorystore import InMemoryStore, InMemoryStoreStatistics

logger = logging.getLogger("utils")


# Hierarchy of data stores starts from the core-data store
# Then the Credential store and the Attachment store.
def initialize_stores():
    if config["mode"] == "dev":
        # All modes shall be in-memory and local by default.
        attachment_storage_type = "local"
        credential_storage_type = "inmemory"
        data_storage_type = "inmemory"  # For DPPs, DPP templates and events
    else:
        attachment_storage_type = config["attachment"]["type"]
        # credential_storage_type = config["credentials"]["type"]
        data_storage_type = config["data"]["type"]  # For DPPs, DPP templates and events

    attachment_store = None
    credential_store = None  # Not implemented for the moment.
    data_store = None

    if attachment_storage_type == "local":
        if config["mode"] == "dev":
            reset = True
        else:
            reset = False
        attachment_store = FileSystemAttachmentStore(config["attachment"], reset=reset)
    else:
        raise NotImplementedError()

    if data_storage_type == "inmemory":
        data_store = InMemoryStore(config["identities"], attachment_store)
        data_store_statistics = InMemoryStoreStatistics(data_store)
    else:
        raise NotImplementedError()

    return data_store, attachment_store, credential_store, data_store_statistics


def import_preseeded_data(
    data_store: BaseDataStore, attachment_store: FileSystemAttachmentStore
):
    # TODO: This must be expanded to be a bit more modular, and
    # Steps
    # 0. Copy filesystem data to filesystem location (primarily attachment data)
    # 1. Import DPPs
    # 2. Import Attachments
    # 3. Import Events
    preseeded_data_path = config["preseeded-data"]["path"]

    preseeded_attachment_data_path = os.path.join(preseeded_data_path, "attachments")
    preseeded_dpp_data_path = os.path.join(preseeded_data_path, "dpps")
    preseeded_dpp_templates_data_path = os.path.join(
        preseeded_data_path, "dpp-templates"
    )

    # Copy attachments
    target_attachment_data_path = config["attachment"]["path"]
    if os.path.exists(target_attachment_data_path):
        # Remove the destination folder if it exists
        shutil.rmtree(target_attachment_data_path)

    # Copy the source folder to the destination
    shutil.copytree(preseeded_attachment_data_path, target_attachment_data_path)
    logger.debug("Copied pre-seeded attachments to the filesystem data folder")

    # Import attachment manifest to attachmentstore
    with open(
        os.path.join(target_attachment_data_path, "attachment_index.json"), "+rb"
    ) as f:
        attachment_manifest = json.loads(f.read())
    attachment_store.import_attachments(attachment_manifest)

    # Import DPP objects, while separating events into their own objects
    for dpp_json_id in os.listdir(preseeded_dpp_data_path):
        with open(os.path.join(preseeded_dpp_data_path, dpp_json_id), "+rb") as f:
            dpp_json = json.loads(f.read())
            import_dpp_into_storage(dpp_json, data_store, attachment_store)
