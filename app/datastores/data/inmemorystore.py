import json
import logging
import random
import uuid
from datetime import datetime
from typing import Any, Dict, List

from app.datamodel.dpp import DigitalProductPassport
from app.datamodel.serde import deserialize_dpp
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore
from app.datastores.data.basedatastore import (
    BaseDataStore,
    DPPResponseContentFormats,
    DPPResponseFormats,
    DPPResponseSignatureFormats,
)

logger = logging.getLogger("Immemorydatastore")


class InMemoryStore(BaseDataStore):
    def __init__(self, identity_config: Dict, attachment_store: BaseAttachmentStore):
        # Structure-> dpp_store[ID] = DigitalProductPassport
        # Structure-> dpp_templates_store[ID][version] = JSONSchema (which is just a Dict)
        # Structure-> event_store[ID] = event_doc (just a Dict)
        # Structure-> credentials_store[ID] = credential_doc (just a Dict)
        self.dpp_store: Dict[str, DigitalProductPassport] = {}
        self.dpp_templates_store: Dict[str, Dict[str, Any]] = {}
        self.event_store: Dict[str, Any] = {}
        self.credentials_store: Dict[str, Any] = {}
        self.attachment_store_ref = attachment_store
        self.identity_config_ref = identity_config

    def get_dpp_document(
        self,
        document_id: str,
        content_format: str = DPPResponseContentFormats.BASE.value,
        format: str = DPPResponseFormats.JSON.value,
        signature_format: str = DPPResponseSignatureFormats.UNSIGNED.value,
    ) -> Dict:
        return deserialize_dpp(
            document_id,
            self,
            self.attachment_store_ref,
            content_format,
            format,
            signature_format,
        )

    def get_dpp_object(self, document_id: str) -> DigitalProductPassport | None:
        return self.dpp_store.get(document_id, None)

    def get_random_dpp_document_id(self) -> str | None:
        return random.choice(list(self.dpp_store.keys()))

    # TODO: Sort by creation date.
    def get_latest_added_dpp_document_id(self) -> str | None:
        return list(self.dpp_store.keys())[-1] if self.dpp_store else None

    def get_dpp_database_metadata(self) -> Dict:
        return {
            "total_dpp_documents": len(self.dpp_store),
            "total_templates": sum(len(v) for v in self.dpp_templates_store.values()),
            "total_events": len(self.event_store),
        }

    # TODO: Implement DPP instantiation
    # def instantiate_dpp(
    #     self, template_id: str, data_mapping: Dict, template_version="latest"
    # ) -> str:
    #     base_path_type = self.identity_config_ref["generation_strategy"][0]
    #     new_dpp_id = base_path_type + ":" + str(uuid.uuid4())
    #     template = self.get_dpp_template(template_id, template_version)
    #     dpp_object = DigitalProductPassport(template_id=template_id, template_version=template_version, data=data_mapping)
    #     self.add_dpp_object(document_id, dpp_object)
    #     return document_id

    # TODO: Implement robust DPP instantiation and validation.
    # def add_dpp_document(
    #     self,
    #     document_id: str,
    #     dpp_document: Dict,
    #     template_id: str | None,
    #     template_version: str | None = "latest",
    # ) -> None:
    #     dpp_object = DigitalProductPassport(**dpp_document)
    #     self.add_dpp_object(document_id, dpp_object)

    # TODO: Implement update method based on DPP class functionality
    # def update_dpp_document(self, document_id: str, dpp_document: str) -> None:
    #     if document_id in self.dpp_store:
    #         dpp_object = self.dpp_store[document_id]
    #         dpp_object.update(dpp_document)  # Assuming DigitalProductPassport class has an update method

    def instantiate_dpp(
        self, template_id: str, data_mapping: Dict, template_version="latest"
    ) -> str:
        raise NotImplementedError

    def add_dpp_document(
        self,
        document_id: str,
        dpp_document: Dict,
        template_id: str | None,
        template_version: str | None = "latest",
    ) -> None:
        raise NotImplementedError

    def update_dpp_document(self, document_id: str, dpp_document: str) -> None:
        raise NotImplementedError

    def add_dpp_object(
        self, document_id: str, dpp_object: DigitalProductPassport
    ) -> None:
        self.dpp_store[document_id] = dpp_object

    def filter_events_full(
        self,
        dpp_id: str,
        dpp_store: Dict[str, DigitalProductPassport],
        event_store: Dict[str, List[Dict]],
        event_type: str = "activity",
    ):
        list_dpp_hierarchy = []

        def traverse(dpp_id):
            list_dpp_hierarchy.append(dpp_id)
            for subpassport in dpp_store[dpp_id].subpassports:
                traverse(subpassport)

        traverse(dpp_id)

        filtered_events_ids_full = set()
        for dpp_id in list_dpp_hierarchy:
            event_id_list = self.dpp_store[dpp_id].events[event_type]

            filtered_events_ids_full.update(event_id_list)
            # filtered_events_full += self.filter_events(dpp_id, event_store)
        filtered_events_full = [
            self.event_store[event] for event in list(filtered_events_ids_full)
        ]
        return filtered_events_full

    def sort_events(self, event_list: List[Dict]) -> List[Dict]:
        # Helper function to extract timestamp
        def extract_timestamp(event: Dict) -> datetime:
            if "prov:atTime" in event:
                return datetime.fromisoformat(
                    event["prov:atTime"]["@value"].replace("Z", "+00:00")
                )
            if "prov:endedAtTime" in event:
                return datetime.fromisoformat(
                    event["prov:endedAtTime"]["@value"].replace("Z", "+00:00")
                )
            return datetime.min  # Return a minimal date if no timestamp found

        # Sort events by timestamp
        sorted_events = sorted(event_list, key=extract_timestamp)
        return sorted_events

    def get_dpp_events(
        self, document_id: str, sorted: bool = True, event_type: str = "activity"
    ) -> List[Dict]:
        event_list = [
            self.event_store[event]
            for event in self.dpp_store[document_id].events[event_type]
        ]
        # event_list = self.filter_events(document_id, self.event_store, event_type)
        return self.sort_events(event_list)

    def get_dpp_full_events(
        self, document_id: str, sorted: bool = True, event_type: str = "activity"
    ) -> List[Dict]:
        event_list = self.filter_events_full(
            document_id, self.dpp_store, self.event_store, event_type
        )
        return self.sort_events(event_list)

    @staticmethod
    def get_id_value(obj):
        if "@id" in obj:
            return obj["@id"]
        elif "id" in obj:
            return obj["id"]
        else:
            raise Exception("Unidentifiable object found.")

    # Add ID if event has no ID.
    def add_dpp_event(
        self, document_id: str, event: Dict, event_type: str = "activity"
    ) -> str | None:
        try:
            event_id = self.get_id_value(event)
        except:
            event_id = str(uuid.uuid4())
            event["id"] = event_id
        if document_id not in self.dpp_store:
            logger.warn(
                "Adding event -> "
                + event_id
                + " with unknown DPP reference -> "
                + document_id
            )
        else:
            # Add event reference to DPP.
            self.dpp_store[document_id].events[event_type].append(event_id)
        if event_id in self.event_store:
            logger.warn("Event was already present.")
        else:
            # Add event to event store.
            self.event_store[event_id] = event
            logger.debug("Event added-> " + event_id)

        return event_id

    def add_dpp_events(
        self, document_id: str, event_list: List[Dict], event_type: List[str] | None
    ) -> List[str | None]:
        if event_type is None:
            event_type = ["activity" for i in range(len(event_list))]
        return [
            self.add_dpp_event(document_id, event, etype)
            for event, etype in zip(event_list, event_type)
        ]

    def update_dpp_event(
        self, document_id: str, event: Dict, event_type: str = "activity"
    ) -> None:
        event_id = self.get_id_value(event)
        # Assume that this event is already in the event_store.
        # Then just overwrite.
        if event_id in self.event_store:
            self.event_store[event_id] = event
        # If not, then something wrong, so throw exception
        else:
            raise Exception("Event not found to update.")

    def delete_dpp_event(
        self, document_id: str, event_id: str, event_type: str = "activity"
    ) -> None:
        # Assume that this event is already in the event_store.
        # Then just delete.
        if event_id in self.event_store:
            del self.event_store[event_id]
        # If not, then something wrong, so throw exception
        else:
            raise Exception("Event not found to delete.")

    def get_event(self, event_id: str) -> Dict | None:
        if event_id in self.event_store:
            return self.event_store[event_id]
        else:
            return None

    # TODO: Handle updating events independently
    def update_event(self, event_id: str, event: Dict) -> None:
        raise NotImplementedError

    # TODO: Handle deleting events independently.
    def delete_event(self, event_id: str) -> None:
        raise NotImplementedError

    def get_event_metadata(self) -> Dict:
        return {
            "total_events": sum(len(events) for events in self.event_store.values()),
        }

    # TODO: Handle all DPP template endpoints
    def get_dpp_template(self, template_id: str, version="latest") -> Dict:
        raise NotImplementedError

    def add_dpp_template(self, template_id: str, json_schema: str) -> str:
        raise NotImplementedError

    def publish_dpp_template(self, template_id: str, version: str) -> None:
        raise NotImplementedError

    def update_dpp_template(self, template_id: str) -> None:
        raise NotImplementedError

    def get_dpp_template_versions_with_metadata(self, template_id: str) -> Dict:
        raise NotImplementedError

    def get_dpp_template_ids_with_metadata(self) -> Dict:
        raise NotImplementedError
