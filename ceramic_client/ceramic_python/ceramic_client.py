# ceramic/ceramic_client.py

import requests
from typing import Any, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)


class CeramicClient:
    def __init__(self, url: str, did):
        self.url = url.rstrip("/")
        self.did = did

    def create_stream_from_genesis(
        self, stream_type_id: int, commit: Dict[str, Any], opts: Dict[str, Any]
    ) -> str:
        payload = {
            "type": stream_type_id,
            "genesis": commit,
            "opts": opts,
        }
        try:
            
            response = requests.post(f"{self.url}/api/v0/streams", json=payload, timeout=10)
            logging.debug(f"Request URL: {f'{self.url}/api/v0/streams'}")
            logging.debug(f"Request Data: {payload}")
            logging.debug(f"Response Status Code: {response.status_code}")
            logging.debug(f"Response Content: {response.content}")
            response.raise_for_status()
            data = response.json()
            return data["streamId"]
        except requests.exceptions.RequestException as e:
            error_message = f"Error creating stream: {str(e)}"
            if response.content:
                error_message += f"\nResponse body: {response.content.decode('utf-8')}"
            logging.error(error_message)
            raise Exception(error_message) from e

    def get_stream_state(self, stream_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.url}/api/v0/streams/{stream_id}")
            response.raise_for_status()
            res = response.json()
            return res.get("state")
        except requests.exceptions.RequestException as e:
            error_message = f"Error getting stream state: {str(e)}"
            if response.content:
                error_message += f"\nResponse body: {response.content.decode('utf-8')}"
            logging.error(error_message)
            raise Exception(error_message) from e

    def get_stream_commits(self, stream_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.url}/api/v0/commits/{stream_id}")
            response.raise_for_status()
            res = response.json()
            genesis_cid_str = res["commits"][0]["cid"]
            previous_cid_str = res["commits"][-1]["cid"]
            return genesis_cid_str, previous_cid_str
        except requests.exceptions.RequestException as e:
            error_message = f"Error getting stream commits: {str(e)}"
            if response.content:
                error_message += f"\nResponse body: {response.content.decode('utf-8')}"
            logging.error(error_message)
            raise Exception(error_message) from e

    def load_stream(self, stream_id: str, opts: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.url}/api/v0/streams/{stream_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Error loading stream: {str(e)}"
            if response.content:
                error_message += f"\nResponse body: {response.content.decode('utf-8')}"
            logging.error(error_message)
            raise Exception(error_message) from e

    def apply_commit(self, stream_id: str, commit: Dict[str, Any], opts: Dict[str, Any]):
        payload = {
            "streamId": stream_id,
            "commit": commit,
            "opts": opts,
        }
        try:
            response = requests.post(f"{self.url}/api/v0/commits", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = f"Error applying commit: {str(e)}"
            if response.content:
                error_message += f"\nResponse body: {response.content.decode('utf-8')}"
            logging.error(error_message)
            raise Exception(error_message) from e