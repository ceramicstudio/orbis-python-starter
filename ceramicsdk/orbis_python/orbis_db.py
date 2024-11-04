from ceramic_python.did import DID
from ceramic_python.ceramic_client import CeramicClient
from ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs
import requests
from typing import Optional
from pathlib import Path
import json

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
        # strip trailing slash
        self.o_endpoint = o_endpoint.rstrip("/")
        self.read_endpoint = self.o_endpoint + "/api/db/query/json"
        self.context_stream = context_stream
        self.table_stream = table_stream
        self.controller = DID(private_key=controller_private_key)
        self.ceramic_client = CeramicClient(c_endpoint, self.controller if self.controller else "")


    @classmethod
    def from_stream(cls, table_stream: Optional[str] = None):
        """Load a read-only db from a stream"""
        return cls(
            context_stream=None,
            table_stream=table_stream,
            controller_private_key=None
        )


    def read(self, env_id: str):
        """Read the db from Ceramic"""
        if not self.table_stream:
            raise ValueError("OrbisDB table stream has not being specified. Cannot read the database.")
        return self.query(env_id, f"SELECT * FROM {self.table_stream}")


    def dump(self, file_path: Path = Path("orbis_db.json")):
        """Dump to json"""
        table = self.read()
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(table, file, indent=4)


    def add_row(self, entry_data):
        """Add a new row to the table"""

        if not self.controller:
            raise ValueError("Read-only database. OrbisDB controller has not being specified. Cannot write to the database.")

        # Check if model requires deterministic (set or single relation)
        model_type = self.ceramic_client.load_stream(self.table_stream, opts={"sync": 0})["state"]["content"]["accountRelation"]["type"]
        is_set_or_single = model_type in ["set", "single"]
        
        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.controller.public_key,
            model=self.table_stream,
            context=self.context_stream,
            deterministic=False
        ) if not is_set_or_single else ModelInstanceDocumentMetadataArgs(
            controller=self.controller.public_key,
            model=self.table_stream,
            context=self.context_stream,
            deterministic=True
        )

        doc = ModelInstanceDocument.create(self.ceramic_client, entry_data, metadata_args) if not is_set_or_single else ModelInstanceDocument.create(
            ceramic_client=self.ceramic_client,
            content=None,  # Must be None for deterministic creation
            metadata_args=metadata_args
        )
        if is_set_or_single:
            doc.replace(entry_data)
        return doc.stream_id


    def update_rows(self, env_id: str, filters: dict, new_content: dict):
        """Update rows"""

        if not self.controller:
            raise ValueError("Read-only database. OrbisDB controller has not being specified. Cannot write to the database.")

        document_ids = [row["stream_id"] for row in self.filter(env_id, filters)]

        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.controller.public_key,
            model=self.table_stream,
            context=self.context_stream,
        )
        return_vals = []
        
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

            item = modelInstance.patch(json_patch=patch, metadata_args=metadata_args, opts={'anchor': True, 'publish': True, 'sync': 0})
            return_vals.append(item)
            
        return return_vals


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
        response = requests.post(url=self.read_endpoint, headers=headers, json=body)
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
        response = requests.post(url=self.read_endpoint, headers=headers, json=body)
        return response.json().get("data", [])


