# main.py

from ceramic.did import DID
from ceramic.ceramic_client import CeramicClient
from ceramic.model_instance_document import (
    ModelInstanceDocument,
    ModelInstanceDocumentMetadataArgs,
    ModelInstanceDocumentMetadata,
)

# Initialize DID and CeramicClient
did = DID(
    id="did:key:z6MkefHJkv4f658zsR59uRAZqCa8wuz8hKJ8VGQUHznN3XB9",
    private_key="e40070a71c32a1b22dbd2123cde261446a9e9d2dfefefef03ec4619697d14eb2",
)
ceramic_client = CeramicClient("http://composedb.env-mainnet:7007", did)

print(did.id , "did")
# Create a new ModelInstanceDocument
metadata_args = ModelInstanceDocumentMetadataArgs(
    controller=did.id,
    model=bytes(bytearray([206,   1,   2,  1, 133,   1,  18,  32, 115, 248,  64,  23, 96,  18,   2, 108, 162, 214, 56, 140,  91, 25, 194, 157,  30,  21, 183, 181, 217,  93, 31,  34,  81, 224,  61, 221, 190, 211, 207, 85])),
)

content = {
    "title": "Alice",
    "createdAt": "2024-09-12T00:50:21.647Z",
    "updatedAt": "2024-09-12T00:50:21.647Z",
}

# Add debug statements before the create call
print("Metadata Args:", metadata_args.controller)
print("Content:", content)

try:
    doc = ModelInstanceDocument.create(ceramic_client, content, metadata_args)
except Exception as e:
    print("Error creating document:", e)
    raise

print(f"Created document with stream ID: {doc.stream_id}")
print(f"Content: {doc.content}")
print(f"Metadata: {doc.metadata.__dict__}")
