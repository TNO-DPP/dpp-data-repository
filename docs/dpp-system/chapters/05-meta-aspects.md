# Meta-aspects and considerations

## Data carriers

- A Data Carrier in DPP terms is usually considered to be the link that connects a physical device to a digital product passport document. The typical example generally used in multiple demos is that of a QR code, that encodes the URL to a Product Passport. Such mechanisms are subject to similar considerations as that of the DPP identifier.
- For instance, a QR code may indicate a single Identifier, or a single URL. Transfer of ownership would either:
- (good case) convert the owner of the Identifier, while still maintaining the same identifier (ideal scenario, may be handled through a DID method such as DID:tdw, or as part of the specifications of the ProductPassport service in a DPP registry.)
- (bad case) add a new data carrier (such as a new QR code as a sticker) representing the new identifier overlapping or adjacent to the old one.
  Examples of other Data Carriers can be RFID tags, NFC chips, 2D Matrices, Barcodes and similar approaches. Some of these are documented in the Battery Pass content guidance document.

## Look up and registry

1. This is a minor aspect, as

## Data format

1. JSON vs JSON-LD vs other formats.
2. Verifiable Credentials and Verifiable Presentations

## Interactions, interfaces and protocols with a DPP system (non-comprehensive - user stories will fill in the rest.)

- Interface format- REST is inevitable. SOAP, JSON-RPC, GraphQL and other approaches cannot deal with the dynamism that such interfacing may require.
- Query resolution
- Protocol for queries, and demonstrating how a specific call for verified data is made

## Templates and creation of data

1. Access control map
2. Instantiation map
3. Static data defaults

## Data integrity and validation

1. JOSE and VC-LDP,
2. Brief introduction to Digital Signatures in general - ECDSA, RSA and others.

## Access control and selective disclosure

1. BBS derived signatures, and SD-JWT approaches

## Decentralized data storage

1. Federations (?) - management of access control?
1. Modes of querying - User interface?
