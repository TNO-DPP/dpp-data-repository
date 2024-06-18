# Introduction and Goals

## Short description of broad goals

Digital Product Passports are currently being developed and mandated by the EU through various pieces of legislation, requiring organizations of all kinds to support the public/restricted availability of product and model data in diverse domains. The purpose of such a process is to enable the following features:

- *Provenance information* - enabling consumers to make a informed choices regarding the origins of their products. This is useful at both model and instance levels.
- *Material composition* - enabling consumers to have reasonable information about the makeup and composition of their products, providing transparency and visibility regarding dangerous and risky materials.
- *Circular economy* - mandating organizations to keep track of their carbon emissions (both in manufacturing and logistics), water usage during manufacturing, waste product generation during manufacturing and recycling/salvaging/destruction, thus enabling regulators and the EU to have greater visibility upon complex supply chains.
- *Certifications and audits* - Enabling an infrastructure for trusted third-party auditors to provide verifiable audits to manufacturing facilities and organizations throughout the supply chain, with either broad or narrow purviews, thus enabling consumers to choose sustainable products sourced from responsible manufacturers. This can include certifications for Slave/Child-labor-free working environments, sustainable farming approaches, safe human working conditions and others.  

## Objective of DPP Backend Repository

The key purpose of the DPP Data Repository (backend) is to manage and host/reference data regarding various types of Digital Product Passports. For this purpose, in this component, the general data model and structure is defined to support files, an event provenance, verifiable credentials, reusable/decentralized identifiers, and a flexible data model system.

### Main technical objectives

It is important that the component support the following features:

- Verifiability (data authenticity, integrity and digital signatures)
- Semantic interoperability (using schemas and knowledge graphs(preferably))
- Decentralization (preferably using federations, thus enabling participants in the ecosystem to be able to manage their own data)
- Robust and granular access-control (thus enabling both or either RBAC and IBAC (Identity))
- Selective disclosure (enabling verifiability using technical means, based on requirement)
