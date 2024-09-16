# ceramic/did.py

import dag_cbor
import json
from base64 import urlsafe_b64encode, b64encode, b64decode
import hashlib

from .helper import sign_ed25519
from multiformats import CID


DAG_CBOR_CODEC_CODE = 113
SHA2_256_CODE = 18


def encode_cid(multihash: bytearray, cid_version:int=1, code:int=DAG_CBOR_CODEC_CODE) -> bytearray:
    """CID encoding"""
    code_offset = 1
    hash_offset = 2
    _bytes = bytearray([0] * (hash_offset + len(multihash)))
    _bytes.insert(0, cid_version)
    _bytes.insert(code_offset, code)
    _bytes[hash_offset:] = multihash
    return _bytes


def create_digest(digest: bytearray, code:int=SHA2_256_CODE) -> bytearray:
    """Create a digest"""
    size = len(digest)
    size_offset = 1
    digest_offset = 2
    _bytes = bytearray([0] * (digest_offset + size))
    _bytes.insert(0, code)
    _bytes.insert(size_offset, size)
    _bytes[digest_offset:] = digest
    return _bytes

def base64UrlEncode(data):
    """"Base64 encoding"""
    return urlsafe_b64encode(data).rstrip(b"=")

def decode_linked_block(linked_block: str) -> dict:
    # Base64 decoding will raise binascii.Error: Incorrect padding if there is not enough padding
    # We can add extra b"=="" to avoid this and the decoder will trim out the unneeded ones. See here:
    # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
    block_bytes = linked_block.encode("utf-8")
    encoded_bytes = b64decode(block_bytes + b"==")
    return dag_cbor.decode(encoded_bytes)

class DID:
    def __init__(self, id: str, private_key: str):
        self.id = id
        self.private_key = private_key

    def as_controller(self):
        return self.id

    def create_dag_jws(self, payload: dict) -> dict:

        encoded_bytes = dag_cbor.encode(data=payload)
        linked_block = b64encode(encoded_bytes).decode("utf-8")

        # SHA256 hash
        hashed = create_digest( bytearray.fromhex(hashlib.sha256(encoded_bytes).hexdigest()) )

        # Create the hash CID
        cid = CID(base="base32", version=1, codec=DAG_CBOR_CODEC_CODE, digest=hashed)
        link = str(cid)

        # Create the payload CID
        cid_bytes = encode_cid(hashed)
        payload_cid = base64UrlEncode(cid_bytes)

        signature_data = json.loads(
            sign_ed25519(
                payload_cid.decode("utf-8"),
                self.id,
                self.private_key
            )
        )
        
        # Construct the signed commit
        return {
            "jws": {
                "payload": payload_cid.decode("utf-8"),
                "link": link,
                "signatures": [{
                    "protected": signature_data["protected"],
                    "signature": signature_data["signature"]
                }],
            },
            "linkedBlock": linked_block
        }
       
        
