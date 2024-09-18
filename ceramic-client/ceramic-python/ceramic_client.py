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
            response = requests.post(f"{self.url}/api/v0/streams", json=payload, timeout=2)
            logging.debug(f"Request URL: {f'{self.url}/api/v0/streams'}")
            logging.debug(f"Request Data: {payload}")
            logging.debug(f"Response Status Code: {response.status_code}")
            logging.debug(f"Response Content: {response.content}")
            response.raise_for_status()
            data = response.json()
            return data["streamId"]
        except Exception as e:
            logging.error(f"Error creating stream: {str(e)}")
            raise

    def get_stream_state(self, stream_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.url}/api/v0/streams/{stream_id}")
            response.raise_for_status()
            res =  response.json()
            return res.get("state")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting stream state: {str(e)}")
            raise

    def load_stream(self, stream_id: str, opts: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.url}/api/v0/streams/{stream_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error loading stream: {str(e)}")
            raise

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
            logging.error(error_message)
            if response.content:
                try:
                    error_details = response.json()
                    error_message += f" Server response: {error_details}"
                except ValueError:
                    error_message += f" Server response: {response.text}"
            raise Exception(error_message) from e
