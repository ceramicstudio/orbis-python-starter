from typing import Optional, List, Union
from dataclasses import dataclass, field
import random
import datetime
import re


PERSONAL_SIGNATURE = "Personal signature"


def base36_encode(number: float) -> str:
    base36 = []
    while number:
        number, remainder = divmod(number, 36)
        base36.append("0123456789abcdefghijklmnopqrstuvwxyz"[remainder])

    return ''.join(reversed(base36))


@dataclass
class SiwxMessage:
    domain: str
    address: str
    statement: Optional[str] = None
    uri: str = ""
    version: str = ""
    nonce: Optional[str] = None
    issuedAt: Optional[str] = None
    expirationTime: Optional[str] = None
    notBefore: Optional[str] = None
    requestId: Optional[str] = None
    chainId: str = ""
    resources: Optional[List[str]] = field(default_factory=list)
    signature: Optional[str] = None
    type: Optional[str] = None

    def __init__(self, param: Union[str, dict]):
        if isinstance(param, str):
            parsed_message = self.from_string(param)
            self.domain = parsed_message['domain']
            self.address = parsed_message['address']
            self.statement = parsed_message.get('statement')
            self.uri = parsed_message['uri']
            self.version = parsed_message['version']
            self.nonce = parsed_message.get('nonce')
            self.issuedAt = parsed_message.get('issuedAt')
            self.expirationTime = parsed_message.get('expirationTime')
            self.notBefore = parsed_message.get('notBefore')
            self.requestId = parsed_message.get('requestId')
            self.chainId = parsed_message['chainId']
            self.resources = parsed_message.get('resources', [])
        else:
            self.__dict__.update(param)

    @staticmethod
    def from_string(param: str) -> dict:
        parsed_data = {}
        patterns = {
            'domain': r"Domain:\s*([^\n]+)",
            'address': r"Address:\s*([^\n]+)",
            'statement': r"Statement:\s*([^\n]+)",
            'uri': r"URI:\s*([^\n]+)",
            'version': r"Version:\s*([^\n]+)",
            'nonce': r"Nonce:\s*([^\n]+)",
            'issued_at': r"Issued At:\s*([^\n]+)",
            'expiration_time': r"Expiration Time:\s*([^\n]+)",
            'not_before': r"Not Before:\s*([^\n]+)",
            'requestId': r"Request ID:\s*([^\n]+)",
            'chainId': r"Chain ID:\s*([^\n]+)",
            'resources': r"Resources:\s*\[\s*([^\]]+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, param, re.MULTILINE)
            if match:
                if key == 'resources':
                    resources_string = match.group(1)
                    resources = [res.strip().strip("'\"") for res in resources_string.split(',')]
                    parsed_data[key] = resources
                else:
                    parsed_data[key] = match.group(1).strip()

        return parsed_data

    def to_message(self, chain: str, address: Optional[str] = None) -> str:
        header = f"{self.domain} wants you to sign in with your {chain} account:"
        address_field = address if address else self.address
        prefix = f"{header}\n{address_field}"

        if not self.nonce:
            self.nonce = base36_encode(random.random() + 1)[4:]

        uri_field = f"URI: {self.uri}"
        version_field = f"Version: {self.version}"
        nonce_field = f"Nonce: {self.nonce}"
        chain_id_field = f"Chain ID: {self.chainId}"

        suffix_array = [uri_field, version_field, chain_id_field, nonce_field]

        if not self.issuedAt:
            self.issuedAt = datetime.datetime.now().isoformat() + "Z"
        suffix_array.append(f"Issued At: {self.issuedAt}")

        if self.expirationTime:
            suffix_array.append(f"Expiration Time: {self.expirationTime}")
        if self.notBefore:
            suffix_array.append(f"Not Before: {self.notBefore}")
        if self.requestId:
            suffix_array.append(f"Request ID: {self.requestId}")
        if self.resources and len(self.resources) > 0:
            resources_field = "Resources:\n" + "\n".join([f"- {resource}" for resource in self.resources])
            suffix_array.append(resources_field)

        suffix = "\n".join(suffix_array)

        if self.statement:
            prefix = f"{prefix}\n\n{self.statement}"

        return f"{prefix}\n\n{suffix}"
