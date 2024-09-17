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
    model="kjzl6hvfrbw6c7wjdc58s11ru9y3h2ubzq6yixqy134xkc63bnnzjcnwaimf711",
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
