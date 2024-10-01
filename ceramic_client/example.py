from ceramic_python.helper import get_iso_timestamp
from ceramic_python.did import DID
from ceramic_python.ceramic_client import CeramicClient
from ceramic_python.model_instance_document import (
    ModelInstanceDocument,
    ModelInstanceDocumentMetadataArgs,
)

def initialize_ceramic():
    did = DID(
        id="did:key:***",
        private_key="***",
    )
    ceramic_client = CeramicClient("http://YOUR_CERAMIC_URL/", did)
    return ceramic_client, did

def create_document():
    ceramic_client, did = initialize_ceramic()
    print(f"Initialized Ceramic client with DID: {did.id}")

    metadata_args = ModelInstanceDocumentMetadataArgs(
        controller=did.id,
        model="kjzl6hvfrbw6c7wjdc58s11ru9y3h2ubzq6yixqy134xkc63bnnzjcnwaimf711",
    )

    content = {
        "title": "First",
        "createdAt": get_iso_timestamp(),
        "updatedAt": get_iso_timestamp(),
    }

    doc = ModelInstanceDocument.create(ceramic_client, content, metadata_args)
    print(f"Stream created with ID: {doc.stream_id}")
    return doc

def update_document(doc):
    new_content ={
        "title": "Second",
        "createdAt": get_iso_timestamp(),
        "updatedAt": get_iso_timestamp(),
    }

    updated_doc = doc.replace(new_content)
    print(f"Stream updated. New content: {updated_doc.content}")
    return updated_doc

def patch_document(doc):
    
    patch = [
        {"op": "replace", "path": "/title", "value": "Patched Title"},
        {"op": "replace", "path": "/updatedAt", "value": get_iso_timestamp()}
    ]
    
    patched_doc = doc.patch(patch)
    print(f"Stream patched. New content: {patched_doc.content}")
    return patched_doc

print(get_iso_timestamp())
# Create a new stream
doc = create_document()

# Update the stream
updated_doc = update_document(doc)

# Patch the stream
patched_doc = patch_document(updated_doc)