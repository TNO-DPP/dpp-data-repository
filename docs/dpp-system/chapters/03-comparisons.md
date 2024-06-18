# Comparisons with other implementations and initiatives

1. Cirpass 2 - our architecture is independently developed and major parallels exist, but user stories are all compatible. _Insert picture of Cirpass 1 architecture_
2. WBCSD - sustainability data model and interactions may fit within attributes section
    - The data model for carbon footprinting is of major interest to integrate as part of the templating layer for product attributes.
3. Spherity - BatteryPass and other general formats, but missing the Access Control layer, the Provenance/Ownership gap considerations, decentralized data storage and merger considerations, event and embedded credential considerations.
4. eIDAS 2.0 - Legal persons are required to have a Digital SSI-type Identity, but implementation is still in progress. This may or may not be extended to represent the identity of organizations in DPPs, as will be described in the DPP infrastructure documentation.
5. Digital Twins and Basyx- Digital Twins are a modern push from Industry 4.0. Currently, many large initiatives consider a Digital Twin to be a Digital Product passport, such as the IDTA, and Tractus-X. While hugely influential, they miss the following considerations

Differences of DPPs from Digital Twins

1. DPPs focus on
    1. Events and provenance
    2. Credentials and SSI identity.
    3. Access control mapping for Role-based and identity based access control
    4. Transfers of ownership
2. Digital Twins focus on
    1. Hierarchy of models
    2. Operations and monitoring, as part of Industry 4.0 objectives

Similarities and useful concepts

1. Registry is a common concept
2. Submodels are useful for manufacturing-type digital product passports, and inspire modular hierarchy in the DPP solution
3. Live data aspects - sensor-based data, static data is easy, but the concept of TimeSeries Data is defined in a modular and usable way [here](https://industrialdigitaltwin.org/wp-content/uploads/2023/03/IDTA-02008-1-1_Submodel_TimeSeriesData.pdf)

The ideal form to deal with this process is the implementation of a DPP-to-DigitalTwin converter, as many of the aspects that are critical to a Digital Twin may be part of the attributes of a DPP. (the reverse cannot be possible, as it would miss a lot of important information)

6. Tractus-X Digital Product Pass - data spaces are potentially a future-scale option to develop Digital Product Passports.

    1. Currently, Data Spaces are intended to offer 3 meta-level functionalities
        1. Identity
        2. Legal contract negotiation aspects
        3. Catalog and resource findability
    2. At this moment, such considerations are not yet a core aspect.
    3. Catena-X considers DPPs as Digital Twins, which bring their own limitations, and do not provide a complete implementation of the possibilities of a DPP solution.
    Future integrations are possible once SIMPL is ready and made available, as an open-source data space integration possibility.

7. ERP systems - currently no integration exists, but DPP systems are not expected to be a manually updated concept. The definition is automated, and integrations with ERP systems should automatically generate the following types of activities:
    
    1. Creation/Manufacturing  - instantiation of a product passport
    2. Sales - transfer of ownership of a product passport.
    3. Salvaging - a workflow/pipeline that destroys a product passport and registers this event

8. A DPP EU registry, other context-specific registries - details are sparse about these initiatives, but the concept of a DPP registry is tentatively considered to be similar to a Digital Twin registry, with a caveat that some additional sustainability-related information needs to be documented in the case of a data providing organization suddenly becoming unavailable to provide that information. Thus, a DPP registry is important to pull and store the required subsets of information that would be strategically relevant for the EU.

9. TRACE4EU - a EBSI-focused provenance initiative that focusses on developing a  provenance solution based on DLT technologies, but stops short of defining it as a DPP solution.

10. TRACE4VALUE - an umbrella of projects developing an ecosystem of DPP implementations in various aspects. Important ones are:
    1. Keep Electronics - a mock UI for what DPP data integrations may look like
        1. Demo - [keep (keepelectronics.com)](https://keepelectronics.com/#/product/PF0H268N)
    2. TrusTrace - a data model for DPP and circularity related data that may be demonstrated for a TShirt product passport. A pilot program wherein QR codes were integrated in manufactured TShirts was completed.
        1. Demo- <https://dpp.marimekko.com/01/06411254897232/21/111>
11. UNTP - UN Traceability Protocol - an independent and parallel initiative that is in progress developing various aspects of a DPP system.
12. Semantic Treehouse - a TNO initiative that enables collaboration in data models development between various organizations.
13. ProPare - end-user focused DPP demo, implementing a mobile-app version of a DPP resolver that hosts some data regarding Digital Product passports.
