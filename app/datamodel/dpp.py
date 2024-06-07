from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from app.datamodel.attachment import AttachmentReference


@dataclass
class InstantiationSource:
    template_id: str
    version: str = "vLatest"


@dataclass
class Facility:
    id: str
    name: str
    address: Optional[str]
    country_code: Optional[str]
    description: Optional[str]


@dataclass
class RepositoryAddress:
    hostname: str


@dataclass
class Entity:
    id: str
    name: str
    full_name: Optional[str]
    facility: Optional[List[Facility] | Facility] = None
    repository_address: Optional[List[RepositoryAddress] | RepositoryAddress] = None
    batch_id: Optional[str] = None


# Design principle: Everything is by reference and pulled from the DataStore.
# No full objects are stored inside a class.
@dataclass
class DigitalProductPassport:
    # This becomes the outer key of the product passport.
    passport_type: str  # Type of DigitalProductPassport. Nothing is ever a simple DigitalProductPassport.

    id: str  # Unique identifier
    title: str  # Title string that contains a basic name for display

    # Optional, could be not recorded as a snub on something.
    instantiated_from: Optional[InstantiationSource]
    manufacturer: Optional[Entity]
    economic_operator: Optional[List[Entity] | Entity]
    current_owner: Optional[Entity]
    known_past_owners: Optional[List[Entity] | Entity]

    registration_id: Optional[str] = None
    batch_id: Optional[str] = None
    creation_timestamp: Optional[str] = None
    destruction_timestamp: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    parent: Optional[str] = None
    # Can start with empty, or can import from existing.
    events: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "activity": [],
            "ownership": [],
        }
    )

    # attributes are flexible, and probably contain all context-specific information.
    # Hence, plain empty dict to start with, but can include other aspects.
    attributes: Dict[str, Any] = field(default_factory=dict)

    # TODO: Credentials are not well-defined right now.
    # May contain direct credentials or string references to a Credential
    credentials: List[Dict | str] = field(default_factory=list)

    # Attachment references should contain this information, even in compact form.
    attachments: List[str] = field(default_factory=list)
    # attachments: List[AttachmentReference] = field(default_factory=list)

    # Subpassports are by default empty, but may contain sub-instantiations.
    subpassports: List[str] = field(default_factory=list)
    # subpassports: List[Union[str, "DigitalProductPassport"]] = field(
    #     default_factory=list
    # )

    # The creation of a DigitalProductPassport instance cannot happen from here, but must instead
    # happen at a store level, in order to distribute templates, events, credentials across locations
    # Thus, no direct deserialization exists.
