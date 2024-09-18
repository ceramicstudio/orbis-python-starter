# Ceramic Py - Python client for Ceramic streams

This Ceramic client implements the payload building, encoding, and signing needed to interact with the [Ceramic Network](https://ceramic.network/). It currently supports `ModelInstanceDocument`.

## Features

- Implements payload building, encoding, and signing for Ceramic interactions
- Currently supports `ModelInstanceDocument`

## Working with Ceramic streams

### Install the Ceramic client using pip

```bash
pip3 install ceramic_python
```

### Create a stream
First, generate a Decentralized Identifier (DID) using a DID library.

```python
from ceramic.helper import get_iso_timestamp
from ceramic.did import DID
from ceramic.ceramic_client import CeramicClient
from ceramic.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs

def initialize_ceramic():
    did = DID(
        id="did:key:z6MkefHJkv4f658zsR59uRAZqCa8wuz8hKJ8VGQUHznN3XB9",
        private_key="e40070a71c32a1b22dbd2123cde261446a9e9d2dfefefef03ec4619697d14eb2",
    )
    ceramic_client = CeramicClient("<CERAMIC_NODE_URL>", did)
    return ceramic_client, did

def create_document():
    ceramic_client, did = initialize_ceramic()

    metadata_args = ModelInstanceDocumentMetadataArgs(
        controller=did.id,
        model="kjzl6hvfrbw6c7wjdc58s11ru9y3h2ubzq6yixqy134xkc63bnnzjcnwaimf711",
    )

    content = {
        "title": "Alice",
        "createdAt": get_iso_timestamp(),
        "updatedAt": get_iso_timestamp(),
    }

    doc = ModelInstanceDocument.create(ceramic_client, content, metadata_args)
    print(f"Stream created with ID: {doc.stream_id}")
    return doc

# Create a new stream
create_document()
```


### Read stream

```python
from ceramic.did import DID
from ceramic.ceramic_client import CeramicClient
from ceramic.model_instance_document import ModelInstanceDocument

def initialize_ceramic():
    did = DID(
        id="did:key:z6MkefHJkv4f658zsR59uRAZqCa8wuz8hKJ8VGQUHznN3XB9",
        private_key="e40070a71c32a1b22dbd2123cde261446a9e9d2dfefefef03ec4619697d14eb2",
    )
    ceramic_client = CeramicClient("<CERAMIC_NODE_URL>", did)
    return ceramic_client, did

def load_document(stream_id):
    ceramic_client, _ = initialize_ceramic()
    doc = ModelInstanceDocument.load(ceramic_client, stream_id)
    print(f"Data from stream: {doc.content}")
    return doc

# Load data from a specific stream
load_document(<STREAM_ID>)

```

### Update stream
```python
from datetime import datetime, timezone
from ceramic.did import DID
from ceramic.ceramic_client import CeramicClient
from ceramic.model_instance_document import ModelInstanceDocument

def initialize_ceramic():
    did = DID(
        id="did:key:z6MkefHJkv4f658zsR59uRAZqCa8wuz8hKJ8VGQUHznN3XB9",
        private_key="e40070a71c32a1b22dbd2123cde261446a9e9d2dfefefef03ec4619697d14eb2",
    )
    ceramic_client = CeramicClient("<CERAMIC_NODE_URL>", did)
    return ceramic_client, did

def update_document(stream_id):
    ceramic_client, _ = initialize_ceramic()
    doc = ModelInstanceDocument.load(ceramic_client, stream_id)

    updated_content = {
        "title": "Bob",
        "updatedAt": get_iso_timestamp(),
    }

    updated = doc.replace(updated_content)
    print(f"Updated data: {updated.content}")
    return updated

# Update an existing stream
update_document(<STREAM_ID>)
```


## For Developement

* Clone this repository
```shell
git clone git@github.com:indexnetwork/ceramic-python.git
cd ceramic-client
```
* Install [Pipenv](https://pipenv.pypa.io/en/latest/).
* Generate the virtual environment:
```shell
make new_env && pipenv shell
```

## Credits

This project is largely based on the work done by the team at https://github.com/valory-xyz/ceramic-py/. We are grateful for their contributions to the Ceramic ecosystem and the open-source community.