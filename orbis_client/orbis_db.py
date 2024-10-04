from ceramic_client.ceramic_python.did import DID
from ceramic_client.ceramic_python.ceramic_client import CeramicClient
from ceramic_client.ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs
import requests
from typing import Optional
from pathlib import Path
import json
from ceramic_client.ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs

class OrbisDB:
    """A relational database stored on OrbisDB/Ceramic"""

    def __init__(
        self,
        c_endpoint: str,
        o_endpoint: str,
        context_stream: Optional[str] = None,
        table_stream: Optional[str] = None,
        controller_private_key: Optional[str] = None
    ) -> None:

        if not table_stream and not controller_private_key:
            raise ValueError("Either the table stream or the controller needs to be specified when instantiating an OrbisDB class")
        self.o_endpoint = o_endpoint
        self.context_stream = context_stream
        self.table_stream = table_stream
        self.controller = DID(controller_private_key) if controller_private_key else None
        self.ceramic_client = CeramicClient(c_endpoint, self.controller.did if self.controller else "")


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


    def query(self, env_id: str, query: str):
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
            "env": env_id
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=self.o_endpoint, headers=headers, json=body)
        return response.json()["data"]


    def filter(self, env_id: str, filters):
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
            "env": env_id
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=self.o_endpoint, headers=headers, json=body)
        return response.json().get("data", [])


