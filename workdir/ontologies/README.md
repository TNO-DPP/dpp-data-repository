# Ontology development

For the moment, the initial unrefined/unversioned versions of ontologies used for the reference implementation are stored here.
At a later moment, these shall be formalized and integrated better into the DPP application, preferably externally stored.

In addition, certain external ontologies are also included for the purpose of reference, for providing input towards events that might be part of a DPP passport.

- GS1 EPCIS 2.0 - <https://ref.gs1.org/standards/epcis/artefacts> - Eventual interoperability with such a standard is necessary.
In addition, the [UNTP](https://uncefact.github.io/spec-untp/docs/specification/TraceabilityEvents/) also has a reference to this [here](https://jargon.sh/user/unece/traceabilityEvents/v/working/artefacts/readme/render)
- PROV-O - Basic ontology supporting Provenance tracking, as a starting point.
- FeDERATED - Provenance tracking in Logistics, though generalizable. Not initially included, but in plans.

An interesting reference for us to reference/consider, by the Pathfinder Provenance Framework is available [here](https://wbcsd.github.io/data-exchange-protocol/v2/)

## Actual ontology

For the purpose of the demo, we already have an idea of the supply chain.

```mermaid
flowchart LR
    A[Supplier 1] -->|Send subcomponents| C[Manufacturer]
    B[Supplier 2] -->|Send subcomponents| C[Manufacturer]
    C[Manufacturer] -->|Send product batches| X[Retailer]
    X -->|Sell| E[End-user 1]
    X -->|Sell| F[End user 2]
    F -->|Send| G[Remanufacturer]
```

In this example, our companies are named the following:

- Supplier 1: SunSparkle Photons Inc. - Photovoltaic Cells
- Supplier 2: SolarEclipse Panels Ltd. - Solar Panel Frames
- Manufacturer: PhotonForge SolarWorks - Solar Panels Manufacturing and Assembly
- Retailer: LuminousOddity Solar Emporium - Retail sales for solar panels
- Remanufacturer: RenewCycle SolarTech GmbH - Remanufacturing facility for old/faulty Solar Panels with observability.

### Event sequences

The optimal-flow sequences are as follows:

#### Photovoltaic Cells Supplier

```mermaid
flowchart LR
    A[Commissioning Event] --> B
    B[Material Preparation Event] --> C
    C[Cell Production Event] --> D
    D[Quality Inspection Event] --> E
    E[Packing Event] --> F
    F[Ownership Transfer Event] --> G[Shipping Event]
```

#### Frame Supplier

```mermaid
flowchart LR
    A[Commissioning Event] --> B
    B[Material Selection Event] --> C
    C[Frame Manufacturing Event] --> D
    D[Coating Application Event] --> E
    E[Quality Check Event] --> F
    F[Packing Event] --> G
    G[Ownership Transfer Event] --> H[Shipping Event]
```

#### Panel Manufacturer

```mermaid
flowchart LR
    X[Batch Receiving Event] --> |Photovoltaic Cells| B
    Y[Batch Receiving Event] --> |Frames| B
    B[Unpacking Event] --> C
    C[Processing Event] --> E
    E[Panel Lamination Event] --> F[Frame Attachment Event]
```

```mermaid
flowchart LR
    F[Frame Attachment Event] --> G
    G[Assembling Event] --> H
    H[Solar Cell Testing Event] --> I
    I[Packing Event] --> T
    T[Ownership Transfer Event] --> U[Shipping Event]
```

#### Retailer

```mermaid
flowchart LR
    A[Batch Receiving Event] --> B
    B[Unpacking Event] --> C
    C[Panel Verification Event] --> D
    D[Inventory Updating Event] --> E[Sales Order Processing Event]
```

```mermaid
flowchart LR
    E[Sales Order Processing Event] --> F
    F[Payment Processing Event] --> G
    G[Packing Event] --> H
    H[OwnershipTransferEvent] --> I[Shipping Event]
```

#### Remanufacturer

```mermaid
flowchart LR
    A[Item Receiving Event] --> B
    B[Schedule Planning Event] --> C
    C[Disassembly Event] --> D
    D[Inspection Event] --> E
    D[Inspection Event] --> F
    D[Inspection Event] --> G
    G[Salvaging Event] --> Z[Return Information Event]
    E[Refurbishing Event] --> H
    F[Part Swapping Event] --> H
    H[Remanufactured Panel Assembly Event] --> I
    I[Packing Event] --> J
    J[Ownership Transfer Event] --> V[Shipping Event]
```

Each of these entities have their own data models for the products that are the core aspect of their business.

## All together now

### Ownership Log

```mermaid
flowchart
    A[PV Cell manufacturer] --> |Creation Event| A
    A[PV Cell manufacturer] --> |Transfer Event| C
    B[Panel Frame Manufacturer] --> |Creation Event| B
    B[Panel Frame Manufacturer] --> |Transfer Event| C
    C[Panel Manufacturer] --> |Creation Event| C
    C[Panel Manufacturer] --> |Transfer Event| D[End User]
    C[Panel Manufacturer] --> |Transfer Event| E
    E[End User] --> |Transfer Event| F[Remanufacturer]
    F --> |Destruction Event| F

    

```

### Event Log (annotated based on who has the data)

```mermaid
flowchart
    A[Commissioning Event] --> |PV Cell manufacturer| B
    B[Material Preparation Event] --> |PV Cell manufacturer|C
    C[Cell Production Event] --> |PV Cell manufacturer|D
    D[Quality Inspection Event] --> |PV Cell manufacturer|E
    E[Packing Event] --> |PV Cell manufacturer| F[Shipping Event]

    G[Commissioning Event] --> |Panel Frame Manufacturer| H
    H[Material Selection Event] --> |Panel Frame Manufacturer|I
    I[Frame Manufacturing Event] --> |Panel Frame Manufacturer|J
    J[Coating Application Event] --> |Panel Frame Manufacturer|K
    K[Quality Check Event] --> |Panel Frame Manufacturer|L
    L[Packing Event] --> |Panel Frame Manufacturer|M[Shipping Event]

    F --> 1
    M --> 2
    1[Batch Receiving Event] --> |PV Cell manufacturer| 3
    2[Batch Receiving Event] --> |Panel Frame Manufacturer| 3
    3[Unpacking Event] --> |Panel Manufacturer| 4
    4[Processing Event] --> |Panel Manufacturer|5
    5[Panel Lamination Event] --> |Panel Manufacturer|6
    6[Frame Attachment Event] --> |Panel Manufacturer|7
    7[Assembling Event] --> |Panel Manufacturer|8
    8[Solar Cell Testing Event] --> |Panel Manufacturer|9
    9[Packing Event] --> |Panel Manufacturer|10[Shipping Event]

    10[Batch Receiving Event] --> |Panel Manufacturer|11
    11[Unpacking Event] --> |Retailer|12
    12[Panel Verification Event] --> |Retailer|13
    13[Inventory Updating Event] --> |Retailer|14
    14[Sales Order Processing Event] --> |Retailer|15
    15[Payment Processing Event] --> |Retailer|16
    16[Packing Event] --> |Retailer to End User 1|17[Shipping Event]
    16[Packing Event] --> |Retailer to End User 2|18[Shipping Event]

    18 --> |Sent to remanufacturer after damn neighbour kids <br/> broke a panel again| 18R
    18R[Item Receiving Event] --> |Remanufacturer| 19
    19[Schedule Planning Event] --> |Remanufacturer|20
    20[Disassembly Event] --> |Remanufacturer|21
    21[Inspection Event] --> |Remanufacturer|24
    21[Inspection Event] --> |Remanufacturer|25
    21[Inspection Event] --> |Remanufacturer|26
    24[Salvaging Event] --> |Remanufacturer|40[Return Information Event]
    25[Refurbishing Event] --> |Remanufacturer|27
    26[Part Swapping Event] --> |Remanufacturer|27
    27[Remanufactured Panel Assembly Event] --> |Remanufacturer|28
    28[Packing Event] --> |Remanufacturer|29[Shipping Event]
```

To support a Provenance Tracking solution, a modification is thus made to adapt their internal data into a message model form based on DPP core ontologies/concepts to make it interoperable with the rest of the ecosystem. To be ideal, the scope of the core ontology must be minimal, as many context-specific standards (for instance, in batteries), as well as function-specific standards (for instance, in events, with GS1 EPCIS, FeDERATED) may come up. A generic non-normative event standard is available with PROV-O, so we use that as a starting point. However, we assume that application-profiles should be defined by each of the end-user organizations or interest groups, to enable true decentralization.

The ontologies in this folder represent an example of ontologies defined by each of these organizations in the supply chain in the previous paragraph, along with the core ontology, and an instance graph for demonstration of a comprehensive full-scale ontology.
