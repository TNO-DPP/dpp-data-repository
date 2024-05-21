from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from app.datamodel.dpp import DigitalProductPassport


class DPPResponseFormats(Enum):
    JSON = "json"
    JSON_LD = "json-ld"


class DPPResponseSignatureFormats(Enum):
    UNSIGNED = "unsigned"
    SELF_SIGNED = "self-signed"
    SIGNED = "signed"


class DPPResponseContentFormats(Enum):
    COMPACT = "compact"
    BASE = "base"
    FULL = "full"
    COMPLETE = "complete"


class BaseDataStore(ABC):
    ### DPPs

    # We need the following interfaces for a Data Store.
    # - Retrieving DPP JSON documents, given a DPP ID (base request) (with local events)
    @abstractmethod
    def get_dpp_document(
        self,
        document_id: str,
        content_format: str = DPPResponseContentFormats.BASE.value,
        format: str = DPPResponseFormats.JSON.value,
        signature_format: str = DPPResponseSignatureFormats.UNSIGNED.value,
    ) -> Dict:
        # Use the deserialization function from serde
        pass

    @abstractmethod
    def get_dpp_object(self, document_id: str) -> DigitalProductPassport:
        pass

    # # - Aggregating and retrieving a full DPP JSON document, given a DPP ID (full request).
    # @abstractmethod
    # def get_dpp_document_full(self, document_id: str):
    #     pass

    # - Specific endpoints to get DPP document IDs of the latest and a random DPP item, specifically for demo purposes
    @abstractmethod
    def get_random_dpp_document_id(self) -> str:
        pass

    @abstractmethod
    def get_latest_added_dpp_document_id(self) -> str:
        pass

    # - Get some data statistics about the content of the database.
    @abstractmethod
    def get_dpp_database_metadata(self) -> Dict:
        pass

    # DPPs - CRUD

    # - Instantiating a DPP instance based on a DPP template (and data mapping), adding to store.
    # By default, the version is latest
    @abstractmethod
    def instantiate_dpp(
        self, template_id: str, data_mapping: Dict, template_version="latest"
    ) -> str:
        # Returns DPP ID, with basic DPP Creation Event, and not much else, except
        # contents of template
        pass

    # Construct an object of references and add it to the store.
    # Assumption is that this is done after ensuring the other sub-aspects have already been added.

    @abstractmethod
    def add_dpp_object(
        self, document_id: str, dpp_object: DigitalProductPassport
    ) -> None:
        pass

    # - (Optional - does it make sense?) Validating a DPP document with a specific template.
    # - Parse an incoming DPP instance and add to store. - may be validated based on template schema.
    @abstractmethod
    def add_dpp_document(
        self,
        document_id: str,
        dpp_document: Dict,
        template_id: Optional[str],
        template_version: Optional[str] = "latest",
    ) -> None:
        pass

    # - Update DPP document
    # Ideally, this should register an update event.
    # Scenarios where this would happen
    # - Adding/removing an attachment
    # - Updating an attribute
    # - Adding a credential
    # Events are managed separately, because they can involve multiple products at once. If added properly, the event will become part of the DPP document when retrieved.
    @abstractmethod
    def update_dpp_document(self, document_id: str, dpp_document: str) -> None:
        pass

    ### EVENTS

    # - Retrieving a list of events (sorted or not) for a DPP document.
    @abstractmethod
    def get_dpp_events(
        self, document_id: str, sorted: bool = True, event_type: str = "activity"
    ) -> List[Dict]:
        pass

    # - Retrieving a list of events (sorted or not) for a full DPP document (including subpassports).
    @abstractmethod
    def get_dpp_full_events(
        self, document_id: str, sorted: bool = True, event_type: str = "activity"
    ) -> List[Dict]:
        pass

    # - Registering an event to a DPP document (assign an ID if ID is not provided).
    @abstractmethod
    def add_dpp_event(
        self, document_id: str, event: Dict, event_type: str = "activity"
    ) -> str | None:
        # Creates an event ID if none exists, uses existing if one is provided
        pass

    # - Registering a batch of events to a DPP document.
    # Importantly, the event should reference all the DPPs it adheres to, and can be added to either of the entities referenced in the Event JSON.
    @abstractmethod
    def add_dpp_events(
        self, document_id: str, event_list: List[Dict], event_type: str = "activity"
    ) -> List[str | None]:
        pass

    # Updating and deleting events, but not in batch, just in-case. Can be updated later if needed.
    @abstractmethod
    def update_dpp_event(
        self, document_id: str, event: Dict, event_type: str = "activity"
    ) -> None:
        pass

    @abstractmethod
    def delete_dpp_event(
        self, document_id: str, event_id: str, event_type: str = "activity"
    ) -> None:
        pass

    # It may be made possible to request a specific event generically, but never to add an event that's not connected
    # to at least one specific DPP ID.
    @abstractmethod
    def get_event(self, event_id: str) -> Dict | None:
        pass

    # Similarly, update and deleting events independently are allowed.
    @abstractmethod
    def update_event(self, event_id: str, event: Dict) -> None:
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> None:
        pass

    # Get some metadata about all events generated so far.
    # TODO: Expand information to include some granularity about types of Events
    @abstractmethod
    def get_event_metadata(self) -> Dict:
        pass

    # - (If supported on the database) - run a custom query of some kind.
    # NOT MENTIONED HERE
    ### DPP TEMPLATES

    # - Retrieving DPP template document, given a DPP template ID and version (default is latest).
    @abstractmethod
    def get_dpp_template(self, template_id: str, version="latest") -> Dict:
        pass

    @abstractmethod
    def add_dpp_template(self, template_id: str, json_schema: str) -> str:
        pass

    # This should create a tag for the template, with the version_id provided.
    @abstractmethod
    def publish_dpp_template(self, template_id: str, version: str) -> None:
        pass

    # Only enable updating the "latest" version, which is the working version, unless published with a tag.
    @abstractmethod
    def update_dpp_template(self, template_id: str) -> None:
        pass

    # Get information about the versions of a template - metadata about aspects as well - this will be documented
    # in the response datamodel
    @abstractmethod
    def get_dpp_template_versions_with_metadata(self, template_id: str) -> Dict:
        pass

    # Get information about the templates available - metadata about versions available as well, and instances created.
    # This will be stored a bit more at a granular level, but aggregated at the higher-level.
    @abstractmethod
    def get_dpp_template_ids_with_metadata(self) -> Dict:
        pass

    # TODO: Handle credentials later, because the signature part may be a bit tricky.
    # @abstractmethod
    # def add_credentials_document(self, credential_id, credential_doc):
    #     pass

    # @abstractmethod
    # def get_credentials_document(self, credential_id):
    #     pass

    # Actually adding the attachments will be handled in a different module (with support for s3 or filesystem), but still based on document_id, or template_id.
    # Adding the attachment link is done in a DPP document update.
    # @abstractmethod
    # def add_attachment(self, attachment_id, file_path):
    #     pass

    # @abstractmethod
    # def get_attachment(self, attachment_id):
    #     pass
