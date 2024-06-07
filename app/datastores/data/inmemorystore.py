import json
import logging
import random
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from app.config import format_multiline_log
from app.datamodel.dpp import DigitalProductPassport, Entity, Facility
from app.datamodel.serde import deserialize_dpp, import_dpp_into_storage
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore
from app.datastores.data.basedatastore import (
    BaseDataStore,
    BaseStoreStatistics,
    DPPResponseContentFormats,
    DPPResponseFormats,
    DPPResponseSignatureFormats,
    FilterConditions,
)

logger = logging.getLogger("in-memory-data")


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
        # dpp_list = list(self.dpp_store.keys())
        # creation_timestamp_list = [self.dpp_store[dpp_id].creation_timestamp for dpp_id in dpp_list]
        dpp_creation_timestamps = [
            (dpp_id, self.dpp_store[dpp_id].creation_timestamp)
            for dpp_id in self.dpp_store.keys()
        ]
        # Filter out entries with None as creation_timestamp and convert the remaining timestamps to datetime objects
        valid_dpp_creation_timestamps = [
            (dpp_id, datetime.strptime(creation_timestamp, "%Y-%m-%dT%H:%M:%SZ"))
            for dpp_id, creation_timestamp in dpp_creation_timestamps
            if creation_timestamp is not None
        ]
        # If no valid timestamps, return None
        if not valid_dpp_creation_timestamps:
            return None
        # log_string = "Timestamps :\n"
        # for i in valid_dpp_creation_timestamps:
        #     log_string += i[0] + " -> " + i[1].isoformat() + "\n"
        # logger.debug(format_multiline_log(log_string))
        latest_dpp_id, _ = max(valid_dpp_creation_timestamps, key=lambda item: item[1])
        return latest_dpp_id

        # return list(self.dpp_store.keys())[-1] if self.dpp_store else None

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
        template_id: str | None = None,
        template_version: str | None = "latest",
    ) -> None:
        import_dpp_into_storage(dpp_document, self, self.attachment_store_ref)

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

    def attach_subpassport_by_id(self, document_id: str, subpassport_id: str) -> None:
        dpp = self.dpp_store.get(document_id, None)
        if dpp is None:
            raise Exception("DPP not available -> " + document_id)
        else:
            subdpp = self.dpp_store.get(subpassport_id, None)
            if subdpp is None:
                raise Exception("Subpassport not available -> " + subpassport_id)
            else:
                dpp.subpassports.append(subpassport_id)
                subdpp.parent = document_id

    def attach_subpassport(self, document_id: str, subpassport_document: Dict) -> None:
        subpassport_document_data = subpassport_document[
            list(subpassport_document.keys())[0]
        ]
        subpassport_id = self.get_id_value(subpassport_document_data)
        self.add_dpp_document(subpassport_id, subpassport_document)
        self.attach_subpassport_by_id(document_id, subpassport_id)

    def detach_subpassport_by_id(self, document_id: str, subpassport_id: str) -> None:
        dpp = self.dpp_store.get(document_id, None)
        if dpp is None:
            raise Exception("DPP not available -> " + document_id)
        else:
            subdpp = self.dpp_store.get(subpassport_id, None)
            if subdpp is None:
                raise Exception("Subpassport not available -> " + subpassport_id)
            else:
                if (
                    subpassport_id not in dpp.subpassports
                    and subdpp.parent != document_id
                ):
                    raise Exception("Subpassport already not attached")
                elif (
                    subpassport_id not in dpp.subpassports
                    and subdpp.parent != document_id
                ):
                    logger.warn("Partially attached subpassport. Detaching fully.")
                    dpp.subpassports = [
                        x for x in dpp.subpassports if x != subpassport_id
                    ]
                    subdpp.parent = ""
                else:
                    dpp.subpassports = [
                        x for x in dpp.subpassports if x != subpassport_id
                    ]
                    subdpp.parent = ""
                    logger.debug(
                        "Subpassport detached from -> "
                        + document_id
                        + ", not removed ->"
                        + subpassport_id
                    )

    # Define helper function to get country code from entity
    @staticmethod
    def get_country_code(entity: Entity):
        if not entity or not entity.facility:
            return "None"
        elif isinstance(entity.facility, list):
            return entity.facility[0].country_code
        else:
            return entity.facility.country_code

    def search_for_dpp(self, filters: FilterConditions) -> List[Dict[str, str]]:
        # Holds the filtered results
        filtered_results = []

        # Iterate through the DPP store
        for id, dpp in self.dpp_store.items():
            match = True

            # Check if name_contains present in ID
            if (
                filters.name_contains
                and filters.name_contains.lower() not in dpp.id.lower()
            ):
                match = False

            # Check passport_type
            if filters.passport_type and dpp.passport_type not in filters.passport_type:
                match = False

            # Check tags
            if filters.tags and not set(filters.tags).issubset(set(dpp.tags)):
                match = False

            # Check batch_id
            if filters.batch_ids and dpp.batch_id not in filters.batch_ids:
                match = False

            # Check registration_id
            if (
                filters.registration_id
                and dpp.registration_id
                and filters.registration_id not in dpp.registration_id
            ):
                match = False

            # Check current_country_codes
            if (
                filters.current_country_codes
                and dpp.current_owner
                and self.get_country_code(dpp.current_owner)
                not in filters.current_country_codes
            ):
                match = False

            # Check origin_country_codes
            if (
                filters.origin_country_codes
                and dpp.manufacturer
                and self.get_country_code(dpp.manufacturer)
                not in filters.origin_country_codes
            ):
                match = False

            if match:
                filtered_results.append({"label": id, "value": id})

        return filtered_results

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


class InMemoryStoreStatistics(BaseStoreStatistics):
    def __init__(self, store: InMemoryStore):
        self.store = store

    def passports_by_batch(self) -> Dict[str, int]:
        batches = defaultdict(int)
        for passport in self.store.dpp_store.values():
            if passport.batch_id:
                batches[passport.batch_id] += 1
        return dict(batches)

    def number_of_batches(self) -> int:
        return len(
            set(
                passport.batch_id
                for passport in self.store.dpp_store.values()
                if passport.batch_id
            )
        )

    def number_of_unique_tags(self) -> int:
        tags = set(
            tag for passport in self.store.dpp_store.values() for tag in passport.tags
        )
        return len(tags)

    def passports_by_tag(self) -> Dict[str, int]:
        tags = defaultdict(int)
        for passport in self.store.dpp_store.values():
            if len(passport.tags) > 0:
                for tag in passport.tags:
                    tags[tag] += 1
                    # batches[passport.batch_id] += 1
        return dict(tags)

    def passports_by_type(self) -> Dict[str, int]:
        passport_types = defaultdict(int)
        for passport in self.store.dpp_store.values():
            passport_types[passport.passport_type] += 1

        return dict(passport_types)

    def number_of_single_passports(self) -> int:
        return sum(
            1
            for passport in self.store.dpp_store.values()
            if not passport.subpassports and not passport.parent
        )

    def number_of_connected_passports(self) -> int:
        return sum(
            1
            for passport in self.store.dpp_store.values()
            if passport.subpassports or passport.parent
        )

    def passports_created_in_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> int:
        return sum(
            1
            for passport in self.store.dpp_store.values()
            if passport.creation_timestamp
            and start_time
            <= datetime.fromisoformat(
                passport.creation_timestamp.replace("Z", "+00:00")
            )
            <= end_time
        )

    def passports_created_last_day(self) -> int:
        now = datetime.now(timezone.utc)
        return self.passports_created_in_time_range(now - timedelta(days=1), now)

    def passports_created_last_week(self) -> int:
        now = datetime.now(timezone.utc)
        return self.passports_created_in_time_range(now - timedelta(weeks=1), now)

    def passports_created_last_month(self) -> int:
        now = datetime.now(timezone.utc)
        return self.passports_created_in_time_range(now - timedelta(days=30), now)

    def passports_created_last_year(self) -> int:
        now = datetime.now(timezone.utc)
        return self.passports_created_in_time_range(now - timedelta(days=365), now)

    def passports_created_last_5_years(self) -> int:
        now = datetime.now(timezone.utc)
        return self.passports_created_in_time_range(now - timedelta(days=365 * 5), now)

    def passports_created_all_time(self) -> int:
        return sum(
            1
            for passport in self.store.dpp_store.values()
            if passport.creation_timestamp
        )

    def events_all_time(self) -> int:
        return len(self.store.event_store.values())

    def number_per_event_type(self) -> Dict[str, int]:
        output = defaultdict(int)

        for event in self.store.event_store.values():
            event_type = event.get("@type", event.get("type", None))
            output[event_type] += 1
        return output

    def to_dict(self):
        passport_stats = {}
        passport_stats["passports_by_batch"] = self.passports_by_batch()
        passport_stats["number_batches"] = self.number_of_batches()
        passport_stats["passports_by_tag"] = self.passports_by_tag()
        passport_stats["number_tags"] = self.number_of_unique_tags()
        passport_stats["passports_by_type"] = self.passports_by_type()
        passport_stats["number_single_passports"] = self.number_of_single_passports()
        passport_stats["number_connected_passports"] = (
            self.number_of_connected_passports()
        )
        passport_stats["passports_created_last_day"] = self.passports_created_last_day()
        passport_stats["passports_created_last_week"] = (
            self.passports_created_last_week()
        )
        passport_stats["passports_created_last_month"] = (
            self.passports_created_last_month()
        )
        passport_stats["passports_created_last_year"] = (
            self.passports_created_last_year()
        )
        passport_stats["passports_created_last_5_years"] = (
            self.passports_created_last_5_years()
        )
        passport_stats["passports_created_all_time"] = self.passports_created_all_time()
        passport_stats["total_dpp_documents"] = (len(self.store.dpp_store),)

        event_stats = {}
        event_stats["events_all_time"] = self.events_all_time()
        event_stats["number_event_types"] = self.number_per_event_type()
        return {"passport": passport_stats, "event": event_stats}
