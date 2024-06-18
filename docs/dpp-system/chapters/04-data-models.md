# Core concepts for an ontology for the Digital Product Passport - v0.5

These concepts are not yet standardized, and attempt to provide a holistic perspective on solving many of the various considerations that are of major interest for a DPP system

## Identity

### Identity of organizations, regulators, individuals(?) and users?

1. The primary participants in DPP systems are not individuals, but organizations. Most of the stakeholders in the user-stories are organizations, and as thus fall under the scope of the eIDAS 2.0 legislation as legal persons.
    1. While this is still in the process of being rolled out, current approaches that organizations can still consider include GLEIF, DIDs and URIs - this can take the form of various options:
        1. privately generating a JWK/secret and using a secrets vault like Oracle or Hashicorp to support and publish such a identity, while integrating control over this secret to perform actions on the rest of the application.
        2. generating an organizational SSI identity in a wallet implementation such as Walt ID or another such option.
    2. Management of these identities is up to the purview of the organization, but custom implementations should consider that employees, ERP systems and other automated DPP integration systems are delegated entities of the organization, and should be considered as thus in updates provided to the DPP solution.

### Identity of DPP

1. GS1 UN/CEFACT seems to use their own identifiers, but the following are types of identifiers that may be enabled.
    - URN or other local ID - no merging possible, and no universal resolvability. Ideal for demo setups and use-cases where custom  resolver, and isolated setups are needed
    - HTTP ID - ID is hosted by the original entity, and needs to be consistently available throughout. Control over the ID may be proven on demand, and used to provide updates to the DPP, and to perform authenticated and authorized actions, but all of this must be managed by the original REO or DPP-hosting solution. May be possible in some situations where the product is not expected to travel through a complex supply chain of sellers and resellers.
    - DID-based ID - Decentralized Identifiers are an ideal use-case wherein the control over the DPP may be easily transferred to multiple entities. However, much depends on the type of the DPP methodology used to provide the DPP. Current implementations available for various aspects of the SSI ecosystem utilize a DID-Web approach.
        - Three aspects are to be considered.
            - DID method : an ID can be generated as needed, using various methods. DID Web is a particularly interesting one, but DID:tdw has some interesting features (with special support for DID document updating, that are particularly appealing for DPP documents)
            - DID controller: assuming a product that can move through an ecosystem, this is the entity (legal or natural) that has an associated private-public keypair that enables usage, control and updates over the data referred to by the DPP. The controller identifier itself does not need to be a DID, but it should be legally a delegated entity of the organization to make changes to the content of the DPP
            - ProductPassport Service:
                - Currently, only Spherity and the BatteryPassport consortium approach DPP documentation this way, and they are the most advanced implementation out there.
                Our proposed extension!
                - convert the ProductPassport extension into a list of servers, rather than a single service. This is a PR proposal for a spec in the DID Spec Registry.
                - there should be information about the current registry as well as previous registries to cover provenance gap scenarios in 3 types of use-cases.
            - Provenance gap handling scenarios
                1. Good use-case - no gap is present. The previous REO directly transfers controller-ship of the DPP to the next data managing entity. This could be an organizational participant that is repurposing, reusing or assembling original product into a different product, but reusing the same identifier and similar product. This is an active process that the REO should support on transfer of ownership of the product, provided the new owner has a compatible ID, and is willing to publish events to the DPP.
                    1. A controller change is not commonly standardized, but is defined in the specification
                2. Moderate use-case - a gap is present in the provenance. The previous REO is known and available. Some functionality is present to register as a user with some proof of ownership of the physical product.  As may be expected, this is highly contextual. For instance, some manner of physical key on the chip enables authentication as a legitimate second-user of the product for registering for a controller change operation. Or a member of a group of trusted entities (verifiable by the REO to be legitimate remanufacturers of the manufactured product type). As in the previous case, this is a controller change, but a passive operation, wherein the REO expects to receive a request for the remanufacturing.
                3. Bad use-case- a gap is present. The previous REO is unavailable (due to bankruptcy or other considerations) or unwilling to change ownership of the product to the new participant. The new participant either
                    1. Creates a new DPP ID with reference to the previous DPP, and aggregate data on user-demand as a unverified source of data. (previously known as)
                    2. Using the same DPP ID is not possible. The DPP ID resolves to the previous entity and will not point to the latest events and updates provided by the new user. This might be overcome if a new Data Carrier (defined in a subsequent section - for now, think QR code)

## General metadata

The following General Metadata is a draft, and this is perhaps the most volatile part of DPP data, since the requirements change significantly per DPP
Currently, we have:
- Title - a string
- instantiated_from - in case a template and version are provided.
- manufacturer- single entity, which contains an ID, Name, and Facility Address, may also contain batch ID for identifying the manufacturing batch if available 
- economic_operator - a list of entities with a similar format as above, but with some information regarding the data repository, as these are entities focused on data hosting. These may be similar to the manufacturer or one of the known past owners, or even a third party providing hosting for a DPP solution.
- current owner - a single entity with a similar format as above
- known_past_owners - a list of entities with a similar format as above
- tags - ways to filter passports down by type.
- registration_id - a generic ID that may be linked to a registration in a common registry
- batch ID - an ID that identifies the current batch if available.
- creation_timestamp - timestamp of creation of DPP by manufacturer. Linked to DPP creation, not necessarily product creation
- destruction_timestamp - timestamp of destruction of DPP by last current owner. Linked to DPP destruction, should ideally be linked to product destruction

The list of values above will definitely evolve, as DPP requirements in legislation are defined further, and the above template may be identified as a component of v0.5 of DPP general metadata.

## Attributes

For this aspect, no clear definitions are provided. Context specific metadata for a product-type may vary significantly, and it is considered that the DPP attributes are flexibly defined by industry specifications.
A few key considerations.

- Types of data held by the DPP:

  - Static data - data that is not expected to change. This may be provided by a template - explained below
  - Time series data- templates for these can be inspired by the structure utilized by the IDTA for Digital Twins.
  - Computed data - this is currently not integrated in the model, but refers to all kinds of continuous sequence evaluations that run computations over a period of data, and then updated as a static value. Examples may be: average battery status, highest number of charges per day of a battery, total carbon emissions through local known lifecycle of a Tshirt.

- Additionally, if required, in the case of infrequent updates to various key values of the DPP data may be documented using the [JSON-patch standard](https://datatracker.ietf.org/doc/html/rfc6902). 

The change in the content of the JSON representing the important values (for example: condition of a TShirt after inspection) Attributes of the DPP may be recorded as an UpdateEvent in the provenance section of the DPP

- To provide some initial examples, 3 attribute sections are defined for 3 types of passports.
  - TShirtPassport - an example of TShirt product passport with a bunch of statistics
  - BatteryProductPassport - an example of a Electric Car Battery with attributes specified in the format of a prior TNO project - GTDE - available publicly [here]([API | TNO Digital Passports (digital-passport.org)](https://docu.digital-passport.org/api/)) (some typos fixed)
  - OscillatorModulePassport - an example of a Toy with a hierarchy of subpassports with their own data content.

## Attachments

Attachments refer to various types of files that may accompany the concept of a DPP. A DPP data repository may reuse the access control for attributes and other aspects to fetch the attachments from the source location of the attachments.

Such data can be model or instance-sourced attachments and may include:

- images, photographs or models
- warranties for specific instances
- user manuals, audit documents and PDF certifications associated with the specific product.
- additional information that may be presented in PDF form, such as disposal and advanced use-instructions

While this is not yet implemented, a few known initiatives for defining resources may be used as a base and extended for the purpose of defining such resources in a semantic format.

1. LDP - Linked Data Platform Resources
2. DCMI/DCAT (less clear.)

As it exists in the backend, a preliminary definition for the concept of Attachments is implemented based on JSON (not JSON-LD), and is fetched directly through the backend.

## Events

Provenance of a product is a tricky and complex subject, and the intent here is to define a flexible skeleton system that supports all manners of context-specific pipelines and workflows.
Events are split into 2 categories

- Ownership Events - defined in a meta (upper) ontology - these are divided into 3 minimal events : CreationEvents, TransferEvents (ownership transfer), DestructionEvents.

These 3 events are generic enough that they may apply to all possible product categories and use-cases. TranferEvents may be skipped if an alternative tracking system is following in the ActivityEvents.

- Activity Events- left flexibly undefined - these events may be defined in any known format.
    This is a domain wherein an integration with the concept of workflows in ERP systems may be useful.
    Some examples of context-specific events are available and integrated in the examples in the Demo. An example for a TShirt Retailer:

  - BatchReceivingEvent -> QualityInspectionEvent -> OrderEvent -> PackagingEvent -> ShippingEvent
3 known event ontologies/vocabularies exist in industry/academia that attempt to provide a generic template structure upon which business processes can be overlaid and extended.
  - W3C Prov-O - This is pure provenance ontology that defines vocabularies to represent actions that are performed by agents. This is the strongest contender and provides a set of very flexible base classes to extend.
  - GS1 EPCIS - EPCIS (Electronic Product Code Information Services) is a global standard that enables businesses to capture and share detailed information about the movement and status of products throughout the supply chain
  - FEDeRATED Events - This is a project started in the context of the Dutch Customs, and is an event ontology designed for shipping and logistics events, but is also similarly extensible to non-logistics cases.
The demo uses Prov-O as the basis to define custom Events for the example passports pre-seeded in the demo.

## Credentials -

1. Credentials are an important aspect of the potential functionality of a DPP. All kinds of scopes and possibilities exist for the purpose of a product's credentials! A credential could be anything supporting a DPP that is issued by a party that is not the current-owner of the DPP.
While not limited to these, some of the possibilities for the implementation of credentials in a DPP are:
1. Instance-level credentials - Information related specifically to a particular product instance. Examples may include Warranties, Documents of sale, Repair and Remanufacturing documentation, etc.
2. Model-level credentials - Information related to a particular product model. Examples could be documentation regarding sustainable manufacturing and carbon emissions in product LCA, Certifications such as IP ratings for smartphones and electronics.
    Potentially - user-manuals, safe disposal documentation, advanced usage manuals, if the data validity is of priority, and these documents are not considered attachments.
1. Facility-level credentials - certifications related to the safe labor practices, human rights certifications and other location-level credentials, typically issued by an auditing organization or governmental regulatory body. The provenance information in the DPP might connect a number of locations for the product for which credentials might be requested.
2. .Organization-level credentials - Credentials such as those provided by the Rainforest Alliance for chocolate manufacturers or the [Global Reporting standards](https://www.globalreporting.org/standards/standards-development/universal-standards/) may be part of the credentials issued by third parties to the Organization
3. Other possible group-level credentials - credentials for products inspected in a batch, a specific human operator, an assembly line in a facility, products created by a specific piece of manufacturing equipment.
1. Rules may be set to automatically attach a credential to a number of products when received, on the basis of conditions. Credentials should also be added manually.

### Format

1. Files such as PDF documents. Some documents may have Digital Signatures attached as manifest. This might integrate standards such as [Qualified Electronic Signatures](https://pdfa.org/pdf-and-digital-signatures/) based on PKI, or Digital Signatures based on standards such as [C2PA](https://c2pa.org/specifications/specifications/1.3/specs/C2PA_Specification.html)
2. (preferably) JSON or other Digital Documents based on Verifiable Credentials. These may be issued by external issuers and associated with a DPP. Such credentials may be stored in an external SSI-based organizational wallet, and referenced in the DPP document, and may be served on demand. In the process flow section, we'll describe how the protocol and flow of requesting a valid credential along with a DPP document can be done.
    - The advantage of using standards like Verifiable Credentials, is the rich ecosystem, and the possibility to create a Verifiable Presentation which can be used to protect against replay attacks.
    - While no yet-popular and direct specifications exist regarding such forms of Credentials issued by organizations, the UNTP has developed the structure of such a credential (work-in-progress), by introducing the concept of a ConformityCredential. Such a credential may contain attestations of various important types, such as Inspections, Audits, Certifications and so on.  

## Hierarchy

1. One of the key and yet unexplored aspects of DPP implementations is the system of hierarchy that can be achieved through a reference-chaining system.
2. In the demo environment, the subpassports are simply referred-to using a simple subpassport connection. This is mirrored in the child passport wherein a reference to the parent is added. (as a json key, not a URI)
3. It may be possible to define more complex forms of DPP associations based on context. For instance, a Battery or Screw could be a modular attachment, while a soldered component such as a capacitor may be more integrated as an attachment. On the roadmap, the subpassport attachment prpoerty may be extended and inherited by context-specific ontologies to integrate a more complex worldview and product-type.
