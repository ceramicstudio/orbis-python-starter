from dotenv import load_dotenv
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from ceramic_python.did import DID
from ceramic_python.ceramic_client import CeramicClient
from ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs
import requests
from key_did_provider_ed25519.src.key_did_provider_ed25519.utils import encode_did
from typing import Optional
from pathlib import Path
import json
from ceramic_client.ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs

load_dotenv()

CERAMIC_ENDPOINT = os.getenv("CERAMIC_ENDPOINT")
ORBIS_ENDPOINT = os.getenv("ORBIS_ENDPOINT")

CONTEXT_ID = os.getenv("CONTEXT_ID")
ENV_ID = os.getenv("ENV_ID")


class CeramicDID:
    """Ceramic DID class wrapper to handle identifiers"""

    def __init__(self, private_key = None) -> None:
        """Contructor"""
        self._private_key = private_key or os.urandom(32).hex()
        self.ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(self._private_key))
        self.ed25519_public_key = self.ed25519_private_key.public_key()
        self._public_key = encode_did(self.ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ))
        self.did = DID(
            id=self._public_key,
            private_key=self._private_key,
        )

    @property
    def private_key(self):
        return self._private_key

    @property
    def public_key(self):
        return self._public_key

    def create_dag_jws(self, payload):
        """Create DAG_JWS"""
        return self.did.create_dag_jws(payload)



class OrbisDB:
    """A relational database stored on OrbisDB/Ceramic"""

    def __init__(
        self,
        context_stream: Optional[str] = None,
        table_stream: Optional[str] = None,
        controller_private_key: Optional[str] = None
    ) -> None:

        if not table_stream and not controller_private_key:
            raise ValueError("Either the table stream or the controller needs to be specified when instantiating an OrbisDB class")

        self.context_stream = context_stream
        self.table_stream = table_stream
        self.controller = CeramicDID(controller_private_key) if controller_private_key else None
        self.ceramic_client = CeramicClient(CERAMIC_ENDPOINT, self.controller.did if self.controller else "")


    @classmethod
    def from_stream(cls, table_stream: Optional[str] = None):
        """Load a read-only db from a stream"""
        return cls(
            context_stream=None,
            table_stream=table_stream,
            controller_private_key=None
        )


    def read(self):
        """Read the db from Ceramic"""
        if not self.table_stream:
            raise ValueError("OrbisDB table stream has not being specified. Cannot read the database.")
        return self.query(f"SELECT * FROM {self.table_stream}")


    def dump(self, file_path: Path = Path("orbis_db.json")):
        """Dump to json"""
        table = self.read()
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(table, file, indent=4)


    def add_row(self, entry_data):
        """Add a new row to the table"""

        if not self.controller:
            raise ValueError("Read-only database. OrbisDB controller has not being specified. Cannot write to the database.")

        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.controller.public_key,
            model=self.table_stream,
            context=self.context_stream
        )

        doc = ModelInstanceDocument.create(self.ceramic_client, entry_data, metadata_args)
        return doc.stream_id


    def update_rows(self, filters, new_content: dict):
        """Update rows"""

        if not self.controller:
            raise ValueError("Read-only database. OrbisDB controller has not being specified. Cannot write to the database.")

        document_ids = [row["stream_id"] for row in self.filter(filters)]

        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.controller.public_key,
            model=self.table_stream,
            context=self.context_stream,
        )

        for document_id in document_ids:
            patch = []

            modelInstance = ModelInstanceDocument.load(self.ceramic_client, stream_id=document_id)
            new_doc = modelInstance.content.copy()

            for key, value in new_content.items():
                new_doc[key] = value
                patch.append({
                    "op": "replace",
                    "path": f"/{key}",
                    "value": value
                })

            modelInstance.patch(json_patch=patch, metadata_args=metadata_args, opts={'anchor': True, 'publish': True, 'sync': 0})

        return len(document_ids)


    def query(self, query: str):
        """Query the database

        Example: SELECT * FROM {TABLE_ID}
        """

        body = {
            "jsonQuery": {
                "$raw": {
                    "query": query,
                    "params": []
                }
            },
            "env": ENV_ID
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=ORBIS_ENDPOINT, headers=headers, json=body)
        return response.json()["data"]


    def filter(self, filters):
        """Filter"""

        filter_list = [f'{key} = {f"'{value}'" if isinstance(value, str) else value}' for key, value in filters.items()]  # strings need to be wrapped around single quotes
        joined_filters = " AND ".join(filter_list)
        query = f"SELECT * FROM {self.table_stream} WHERE {joined_filters}"

        body = {
            "jsonQuery": {
                "$raw": {
                    "query": query,
                    "params": []
                }
            },
            "env": ENV_ID
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=ORBIS_ENDPOINT, headers=headers, json=body)
        return response.json().get("data", [])



# Setup a table stream and a private key for the DID
table_stream = "kjzl6hvfrbw6c6adsnzvbyr6itmf0igfy25xu0mqzei2pe2xw1hlusqyuknb9ky"
did_pkey = os.urandom(32).hex()

# Instantiate a read-only db
db = OrbisDB.from_stream(table_stream)

# Read the whole db
print(db.read())

# Instantiate a read and write db
db = OrbisDB(context_stream=CONTEXT_ID, table_stream=table_stream, controller_private_key=did_pkey)

# Add a new row
db.add_row({"user_id": 2, "user_name": "test_user_3", "user_points": 1000})

# Select some rows
print(db.filter({"user_points": 1000}))

# Update a row batch
db.update_rows(filters={"user_name": "test_user_3"}, new_content={"user_points": 2000})

# Dump the db to a local json file
db.dump()
