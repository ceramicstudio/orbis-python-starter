import base64
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
import os

from .codecs import DagJWS


def random_string() -> str:
    return base64.b64encode(os.urandom(16)).decode('utf-8')


def encode_base64(bytes_data: bytes) -> str:
    return base64.b64encode(bytes_data).decode('utf-8')


def encode_base64_url(bytes_data: bytes) -> str:
    return base64.urlsafe_b64encode(bytes_data).decode('utf-8')


def decode_base64(s: str) -> bytes:
    return base64.b64decode(s.encode('utf-8'))


def base64url_to_json(s: str) -> Dict[str, Any]:
    decoded_bytes = base64.urlsafe_b64decode(s.encode('utf-8'))
    return json.loads(decoded_bytes.decode('utf-8'))


def did_with_time(did: str, at_time: Optional[datetime] = None) -> str:
    if at_time:
        version_time = at_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        return f"{did}?versionTime={version_time}"
    else:
        return did


def from_dag_jws(jws: DagJWS) -> str:
    if len(jws.signatures) > 1 or len(jws.signatures) == 0:
        raise ValueError('Cant convert to compact jws')

    return f"{jws.signatures[0].protected}.{jws.payload}.{jws.signatures[0].signature}"


def extract_controllers(controller_property: Union[str, List[str], None]) -> List[str]:
    if controller_property:
        if isinstance(controller_property, list):
            return controller_property
        else:
            return [controller_property]
    else:
        return []
