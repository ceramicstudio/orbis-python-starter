from dotenv import load_dotenv
import os
from pprint import pprint
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from ceramic_python.did import DID
from ceramic_python.ceramic_client import CeramicClient
from ceramic_python.model_instance_document import ModelInstanceDocument, ModelInstanceDocumentMetadataArgs
import requests
from key_did_provider_ed25519.utils import encode_did

load_dotenv()

ENV_ID = os.getenv("ENV_ID")
TABLE_ID = os.getenv("TABLE_ID")
CONTEXT_ID = os.getenv("CONTEXT_ID")
AGENT_ONE_SEED = os.getenv("AGENT_ONE_SEED")
AGENT_TWO_SEED = os.getenv("AGENT_TWO_SEED")
AGENT_THREE_SEED = os.getenv("AGENT_THREE_SEED")
CERAMIC_ENDPOINT = os.getenv("CERAMIC_ENDPOINT")
ORBIS_ENDPOINT = os.getenv("ORBIS_ENDPOINT")

switcher = {
"agent_one": AGENT_ONE_SEED,
"agent_two": AGENT_TWO_SEED,
"agent_three": AGENT_THREE_SEED
}

class CeramicActions:

    def __init__(self, agent):
        self.private_key = switcher.get(agent)
        self.ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(self.private_key))
        self.ed25519_public_key = self.ed25519_private_key.public_key()
        self.did = encode_did(self.ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ))
    
    def initialize_ceramic(self):
        did = DID(
            id=self.did,
            private_key=self.private_key,
        )
        ceramic_client = CeramicClient(CERAMIC_ENDPOINT, did)
        return ceramic_client

    def create_document(self, content):
        ceramic_client = self.initialize_ceramic()
        pprint(f"Initialized Ceramic client with DID: {self.did}")

        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.did,
            model=TABLE_ID,
            context=CONTEXT_ID
        )
        
        # Get the current date and time in UTC
        current_time = datetime.now(timezone.utc)

        # Format it as an ISO 8601 string
        formatted_time = current_time.isoformat()
        
        content.update({
            # get datetime
            "timestamp": formatted_time,
        })

        doc = ModelInstanceDocument.create(ceramic_client, content, metadata_args)
        pprint(f"Stream created with ID: {doc.stream_id}")
        return doc
    
    def get_all_documents(self):

        body = {
            "jsonQuery": {
                "$raw": {
                    "query": f"SELECT * FROM {TABLE_ID}",
                    "params": []
                }
            },
            "env": ENV_ID
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=ORBIS_ENDPOINT, headers=headers, json=body)
        pprint(response.json())
        return response.json()
    
    def get_with_filter(self, filter):
        
        filters = []
        for (key, value) in filter.items():
            filter = f"{key} = {value}"
            filters.append(filter)
            
        # Join the filters with 'AND' if there are multiple filters
        joined_filters = " AND ".join(filters)
        
        body = {
            "jsonQuery": {
                "$raw": {
                    "query": f"SELECT * FROM {TABLE_ID} WHERE {joined_filters}",
                    "params": []
                }
            },
            "env": ENV_ID
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=ORBIS_ENDPOINT, headers=headers, json=body)
        pprint(response.json())
        return response.json()
    
    def update_document(self, document_id, content):
        ceramic_client = self.initialize_ceramic()
        pprint(f"Initialized Ceramic client with DID: {self.did}")

        metadata_args = ModelInstanceDocumentMetadataArgs(
            controller=self.did,
            model=TABLE_ID,
            context=CONTEXT_ID,
        )
        
        # Get the current date and time in UTC
        current_time = datetime.now(timezone.utc)

        # Format it as an ISO 8601 string
        formatted_time = current_time.isoformat()
        
        content.update({
            # get datetime
            "timestamp": formatted_time,
        })
        
        patch =[]
        
        modelInstance = ModelInstanceDocument.load(ceramic_client, stream_id=document_id)
        new_doc = modelInstance.content.copy()

        for key, value in content.items():
            new_doc[key] = value
            patch.append({
                "op": "replace",
                "path": f"/{key}",
                "value": value
            })
        
        modelInstance.patch(json_patch=patch, metadata_args=metadata_args, opts={'anchor': True, 'publish': True, 'sync': 0})
        
        # get updated state
        new_state = ModelInstanceDocument.load(ceramic_client, stream_id=document_id).content

        pprint(f"Stream updated with ID: {document_id}")
        return new_state