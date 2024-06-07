import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from app.config import format_multiline_log
from app.datamodel.attachment import AttachmentReference
from app.datamodel.dpp import DigitalProductPassport, Entity
from app.datastores.attachments.baseattachmentstore import BaseAttachmentStore
from app.datastores.data.basedatastore import (
    BaseDataStore,
    DPPResponseContentFormats,
    DPPResponseFormats,
    DPPResponseSignatureFormats,
)

logger = logging.getLogger("serde")
# Contains all utility functions to serialize and deserialize into the datamodels and add to the stores.

# Deserialization -
# this is primarily used for the pre-seeded data, but there may also be a need
#   to integrate information from multiple sources that return a complementary set of data.
# Purposes: Pre-seeded data, federation response integration
# For the sake of clarity and verifiability, different datastores are set up to accommodate
#   information from other sources
# Parts
# 1. (DONE) Parsing AttachmentReferences (potentially from a AttachmentIndex, otherwise ReferenceIDs have to be refreshed in the DPP and templates)
#       -> Directly integrated in FilesystemAttachmentStore - future work may support RBAC on top of external stores
# 2. (TODO) Parsing DPP-templates across versions - if metadata is not present, it begins from v0 (also vLatest).
# 3. Parsing DPPs - while going through these, the content of the events and credentials are integrated first
#       DPP -> Event  resolution is a thing, Event -> DPP is more informative of the string.

# Potential bug: in case of restarting of DPP backend, sync issues may require updating of the unique IDs
# def generate_indices_and refresh_dpps():


def import_dpp_into_storage(
    input_dict,
    data_store: BaseDataStore,
    attachment_store: BaseAttachmentStore,
    parent_id=None,
):

    # Data store imports
    # Attachment store compares and identifies conflicts - with priority on DPP data,
    #   if the link matches
    passport_type = list(input_dict.keys())[0]
    passport_data = input_dict[passport_type]
    passport_id = passport_data["id"]
    passport_obj = DigitalProductPassport(
        passport_type=passport_type,
        id=passport_id,
        title=passport_data["title"],
        manufacturer=passport_data.get("manufacturer", None),
        economic_operator=passport_data.get("economic_operator", None),
        current_owner=passport_data.get("current_owner", None),
        known_past_owners=passport_data.get("known_past_owners", []),
        tags=passport_data.get("tags", []),
        registration_id=passport_data.get("registration_id", None),
        batch_id=passport_data.get("batch_id", None),
        creation_timestamp=passport_data.get("creation_timestamp", None),
        destruction_timestamp=passport_data.get("destruction_timestamp", None),
        instantiated_from=passport_data.get("instantiated_from", None),
        attributes=passport_data["attributes"],  # Anything inside goes in as-is
        credentials=passport_data[
            "credentials"
        ],  # For now, this is not specifically defined.
    )

    # Attachments
    # Process: first check if the attachment is already present with the right ID in the store.
    # TODO: if not present, also check the data to identify if something exists where it should
    attachment_ids_to_store: List[str] = []
    for input_attachment in passport_data["attachments"]:
        if type(input_attachment) is str:
            if input_attachment in attachment_store.attachments_index:
                attachment_ids_to_store.append(input_attachment)
            # will be an object otherwise
        else:
            try:
                input_attachment_id = input_attachment["attachment_id"]
                if input_attachment_id in attachment_store.attachments_index:
                    # Found existing refernece, check if path/file exist
                    path = attachment_store.attachments_index[input_attachment_id].path
                    if path is not None and Path(path).is_file():
                        attachment_ids_to_store.append(input_attachment_id)
                else:
                    logger.error(
                        "No file found for importing attachment "
                        + input_attachment_id
                        + " for "
                        + passport_id
                    )
                    logger.error("Try uploading manually at an endpoint.")
            except Exception as e:
                logger.error("Cannot read attachment data for " + passport_id)
    # Log number of attachments found.
    logger.debug(
        "Found " + str(len(attachment_ids_to_store)) + " attachments for " + passport_id
    )

    # Register in passport object
    passport_obj.attachments = attachment_ids_to_store

    def get_id_value(obj):
        if "@id" in obj:
            return obj["@id"]
        elif "id" in obj:
            return obj["id"]
        else:
            raise Exception("Unidentifiable object found.")

    # Subpassports
    subpassport_ids_to_store: List[str] = []
    # Recursive calls for hierarchical objects
    for subpassport in passport_data["subpassports"]:
        if type(subpassport) is str:
            logger.debug("Attempting subpassport import (ref) ->" + subpassport)
            # check store for existing passport
            if data_store.get_dpp_document(subpassport) is None:
                logger.error(
                    "Cannot find subpassport. Continuing to import remaining subpassports."
                )
        else:
            try:
                assert type(subpassport) == dict
                subpassport_type = list(subpassport.keys())[0]
                subpassport_id = get_id_value(subpassport[subpassport_type])
                logger.debug(
                    "Attempting subpassport import (obj) -> "
                    + subpassport_type
                    + " -> "
                    + subpassport_id
                )
                import_dpp_into_storage(subpassport, data_store, attachment_store)
                subpassport_ids_to_store.append(subpassport_id)
            except Exception as e:
                raise Exception("Unable to parse subpassport for " + passport_id)

    # Assigning identified objects to each other
    passport_obj.subpassports = subpassport_ids_to_store
    for subpassport_id in subpassport_ids_to_store:
        subpassport = data_store.get_dpp_object(subpassport_id)
        subpassport.parent = passport_id

    data_store.add_dpp_object(passport_id, passport_obj)
    logger.info(
        "Successfully added "
        + passport_data["title"]
        + " -> "
        + passport_id
        + " to the store."
    )

    # Events
    activity_event_ids_to_store: List[str] = []
    ownership_event_ids_to_store: List[str] = []
    try:
        input_activity_events: List = passport_data["events"]["activity"]
        input_ownership_events: List = passport_data["events"]["ownership"]
    except:
        logger.error("Cannot read events for " + passport_id)
    for event in input_activity_events:
        try:
            event_id = get_id_value(event)
            activity_event_ids_to_store.append(event_id)
            # TODO: better validation of existing events.
            # Current handling, prefer existing event in the Event store
            if data_store.get_event(event_id) is None:
                try:
                    data_store.add_dpp_event(passport_id, event, "activity")
                except Exception as e:
                    logger.error("Error adding DPP event " + event_id + "-" + str(e))
            else:
                existing_event = data_store.get_event(event_id)
                try:
                    assert existing_event == event
                except:
                    logger.error(
                        "Input activity event different from existing added event with the same ID ->"
                        + event_id
                    )
        except Exception as e:
            print(e)
            logger.error("Cannot find ID for activity event in " + passport_id)

    # input()

    for event in input_ownership_events:
        try:
            event_id = get_id_value(event)
            ownership_event_ids_to_store.append(event_id)
            # TODO: better validation of existing events.
            # Current handling, prefer existing event in the Event store
            if data_store.get_event(event_id) is None:
                try:
                    data_store.add_dpp_event(passport_id, event, "ownership")
                except Exception as e:
                    logger.error("Error adding DPP event " + event_id + "-" + str(e))
            else:
                existing_event = data_store.get_event(event_id)
                try:
                    assert existing_event == event
                except:
                    logger.error(
                        "Input ownership event different from existing added event with the same ID ->"
                        + event_id
                    )
        except:
            logger.error("Cannot find ID for ownership event in " + passport_id)

    # Log number of events found.
    logger.debug(
        "Found "
        + str(len(activity_event_ids_to_store))
        + " activity events for "
        + passport_id
    )
    logger.debug(
        "Found "
        + str(len(ownership_event_ids_to_store))
        + " ownership events for "
        + passport_id
    )

    # Add references to DPP object
    passport_obj.events = {
        "activity": activity_event_ids_to_store,
        "ownership": ownership_event_ids_to_store,
    }
    logger.debug(
        format_multiline_log(
            json.dumps(data_store.get_dpp_database_metadata(), indent=4)
        )
    )
    # logger.debug(
    #     format_multiline_log(
    #         json.dumps(
    #             deserialize_dpp(
    #                 passport_id,
    #                 data_store,
    #                 attachment_store,
    #                 "compact",
    #                 "json-ld",
    #                 # passport_id, data_store, attachment_store, "base", "json"
    #                 # passport_id, data_store, attachment_store, "full", "json"
    #                 # passport_id, data_store, attachment_store, "complete", "json"
    #                 # passport_id, data_store, attachment_store, "base", "json"
    #             ),
    #             indent=4,
    #         )
    #     )
    # )


# Serialization
# This is the core code that the API interfaces use. They interact with a provided store, and respond with multiple forms
# of DPP information.

#     UNSIGNED = "unsigned"
#     SELF_SIGNED = "self-signed"
#     SIGNED = "signed" - return JSON-LD VC form with schema, enveloped VPs

# class DPPResponseFormats(Enum):
#     JSON = "json"
#     JSON_LD = "json-ld"
# class DPPResponseSignatureFormats(Enum):
#     UNSIGNED = "unsigned" - return unsigned form either JSON or JSON-LD
#     SELF_SIGNED = "self-signed" - return JWT or JSON-LD LDP VC form signature (optional schema)
#     SIGNED = "signed"
# class DPPResponseContentFormats(Enum):
#     COMPACT = "compact" - return simple JSON with only references to other aspects, no credentials
#     BASE = "base" - return JSON with attachments and references to other aspects
#     FULL = "full" - return JSON with expanded subpassports
#     COMPLETE = "complete" - return JSON with expanded subpassports all the way down

# TODO: Integrate PyJWT, SD-JWT, VC-JOSE-JWT


def prepare_dpp_response_content(
    dpp_object: DigitalProductPassport,
    data_store: BaseDataStore,
    attachment_store: BaseAttachmentStore,
    content_format: str,
) -> Dict:
    output_content = {}
    dpp_type = dpp_object.passport_type
    output_content[dpp_type] = {
        "id": dpp_object.id,
        "title": dpp_object.title,
        "attributes": dpp_object.attributes,
        "credentials": dpp_object.credentials,  # Handle this at a later time.
        "current_owner": dpp_object.current_owner,
        "known_past_owners": dpp_object.known_past_owners,
        "manufacturer": dpp_object.manufacturer,
        "economic_operator": dpp_object.economic_operator,
        "tags": dpp_object.tags,
        "registration_id": dpp_object.registration_id,
        "batch_id": dpp_object.batch_id,
        "creation_timestamp": dpp_object.creation_timestamp,
        "destruction_timestamp": dpp_object.destruction_timestamp,
        "parent": dpp_object.parent,  # Reference to parent
    }
    if content_format == DPPResponseContentFormats.COMPACT.value:
        output_content[dpp_type]["attachments"] = dpp_object.attachments
        output_content[dpp_type]["events"] = dpp_object.events
        output_content[dpp_type]["subpassports"] = dpp_object.subpassports
    elif content_format == DPPResponseContentFormats.BASE.value:
        output_content[dpp_type]["attachments"] = []

        # Retrieve attachments
        for attachment_id in dpp_object.attachments:
            attachment_object: AttachmentReference = attachment_store.attachments_index[
                attachment_id
            ]
            output_content[dpp_type]["attachments"].append(
                attachment_object.to_public_dict()
            )
        output_content[dpp_type]["events"] = {"activity": [], "ownership": []}

        # Retrieve activity and ownership events
        output_content[dpp_type]["events"]["activity"] += data_store.get_dpp_events(
            dpp_object.id, event_type="activity"
        )
        output_content[dpp_type]["events"]["ownership"] += data_store.get_dpp_events(
            dpp_object.id, event_type="ownership"
        )
        # Keep references to subpassports
        output_content[dpp_type]["subpassports"] = dpp_object.subpassports

    elif content_format == DPPResponseContentFormats.FULL.value:
        output_content[dpp_type]["attachments"] = []

        # Retrieve attachments
        for attachment_id in dpp_object.attachments:
            attachment_object: AttachmentReference = attachment_store.attachments_index[
                attachment_id
            ]
            output_content[dpp_type]["attachments"].append(
                attachment_object.to_public_dict()
            )
        output_content[dpp_type]["events"] = {"activity": [], "ownership": []}

        # Retrieve activity and ownership events
        output_content[dpp_type]["events"]["activity"] += data_store.get_dpp_events(
            dpp_object.id, event_type="activity"
        )
        output_content[dpp_type]["events"]["ownership"] += data_store.get_dpp_events(
            dpp_object.id, event_type="ownership"
        )
        # Get basic deserializations of subpassports
        output_content[dpp_type]["subpassports"] = []
        for subpassport_id in dpp_object.subpassports:
            sub_dpp_object = data_store.get_dpp_object(subpassport_id)
            output_content[dpp_type]["subpassports"].append(
                prepare_dpp_response_content(
                    sub_dpp_object,
                    data_store,
                    attachment_store,
                    DPPResponseContentFormats.BASE.value,
                )
            )
    elif content_format == DPPResponseContentFormats.COMPLETE.value:
        output_content[dpp_type]["attachments"] = []

        # Retrieve attachments
        for attachment_id in dpp_object.attachments:
            attachment_object: AttachmentReference = attachment_store.attachments_index[
                attachment_id
            ]
            output_content[dpp_type]["attachments"].append(
                attachment_object.to_public_dict()
            )
        output_content[dpp_type]["events"] = {"activity": [], "ownership": []}

        # Retrieve activity and ownership events
        output_content[dpp_type]["events"]["activity"] += data_store.get_dpp_events(
            dpp_object.id, event_type="activity"
        )
        output_content[dpp_type]["events"]["ownership"] += data_store.get_dpp_events(
            dpp_object.id, event_type="ownership"
        )
        # Get basic deserializations of subpassports
        output_content[dpp_type]["subpassports"] = []
        for subpassport_id in dpp_object.subpassports:
            sub_dpp_object = data_store.get_dpp_object(subpassport_id)
            output_content[dpp_type]["subpassports"].append(
                prepare_dpp_response_content(
                    sub_dpp_object,
                    data_store,
                    attachment_store,
                    DPPResponseContentFormats.COMPLETE.value,
                )
            )
    else:
        raise Exception("Invalid content format for deserialization")
    return output_content


def deserialize_dpp(
    dpp_id,
    data_store: BaseDataStore,
    attachment_store: BaseAttachmentStore,
    content_format: str,
    format: str,
    # TODO: Handle signatures with pyJWT and others.
    signature_format: str = DPPResponseSignatureFormats.UNSIGNED.value,
) -> Dict:
    output_content = {}
    dpp_object: DigitalProductPassport = data_store.get_dpp_object(dpp_id)

    # TODO: Current assumption, JSON content within. To expand to JSON-LD content
    output_content: Dict = prepare_dpp_response_content(
        dpp_object, data_store, attachment_store, content_format
    )

    if format == DPPResponseFormats.JSON.value:
        pass
    elif format == DPPResponseFormats.JSON_LD.value:
        wrapper: Dict[str, Any] = {"@context": ["https://www.w3.org/ns/credentials/v2"]}
        wrapper["id"] = dpp_object.id
        wrapper["type"] = [dpp_object.passport_type, "DigitalProductPassport"]
        # TODO: Identify the latest owner of the product from the ownership log.

        if dpp_object.current_owner is not None:
            current_owner: Entity = dpp_object.current_owner
            wrapper["issuer"] = current_owner.id
        else:
            wrapper["issuer"] = "unknown"

        # TODO: Identify the dpp:CreationEvent and the time of the event.
        if dpp_object.creation_timestamp is not None:
            wrapper["validFrom"] = dpp_object.creation_timestamp
        else:
            wrapper["validFrom"] = "2000-01-01T12:00:00Z"
        wrapper["credentialSubject"] = output_content
        output_content = wrapper

    return output_content

    # format_json_cases = ["compact", "base", "full"]
    # format_jsonld_cases = ["unsigned", "self-signed", "signed"]
    # if format in format_json_cases:
    #     deserialize_dpp_to_json(dpp_object, data_store, attachment_store)
    # elif format in format_jsonld_cases:
    #     deserialize_dpp_to_jsonld(dpp_object, data_store, attachment_store)
