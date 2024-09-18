# ceramic/helper.py

import hashlib
import os
from datetime import datetime, timezone, UTC
from multiformats.multibase import base36
from base64 import urlsafe_b64encode, b64encode, b64decode
from jwcrypto import jwk, jws
from jwcrypto.common import json_encode, base64url_encode, base64url_decode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

DAG_CBOR_CODEC_CODE = 113
SHA2_256_CODE = 18


def encode_cid(
    multihash: bytearray, cid_version: int = 1, code: int = DAG_CBOR_CODEC_CODE
) -> bytearray:
    """CID encoding"""
    code_offset = 1
    hash_offset = 2
    _bytes = bytearray([0] * (hash_offset + len(multihash)))
    _bytes.insert(0, cid_version)
    _bytes.insert(code_offset, code)
    _bytes[hash_offset:] = multihash
    return _bytes


def create_digest(digest: bytearray, code: int = SHA2_256_CODE) -> bytearray:
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
    """Base64 URL-safe encoding"""
    return urlsafe_b64encode(data).rstrip(b"=")


def sign_ed25519(payload: dict, did: str, seed: str):
    """Sign a payload using EdDSA (ed25519)"""

    payload_b64decoded = base64url_decode(payload)

    # Create an ed25519 from the seed
    key_ed25519 = Ed25519PrivateKey.from_private_bytes(bytearray.fromhex(seed))

    # Derive the public and private keys
    # private key
    d = base64url_encode(
        key_ed25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
    )

    # public key
    x = base64url_encode(
        key_ed25519.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw
        )
    )

    # Create a JWK key compatible with the jwcrypto library
    # https://jwcrypto.readthedocs.io/en/latest/jwk.html#classes
    # To create a random key: key = jwk.JWK.generate(kty='OKP', size=256, crv='Ed25519')
    key = jwk.JWK(
        **{
            "crv":"Ed25519",
            "d": d, # private key
            "kty":"OKP",
            "size":256,
            "x": x,  # public key
        }
    )

    # Create the JWS token from the payload
    jwstoken = jws.JWS(payload_b64decoded)

    # Sign the payload
    # https://github.com/latchset/jwcrypto/blob/fcdc7d76b5a5924f9343a92b2627944a855ae62a/jwcrypto/jws.py#L477
    jwstoken.add_signature(
        key=key,
        alg=None,
        protected=json_encode({"alg": "EdDSA", "kid": did + "#" + did.split(":")[-1]}),
    )

    signature_data = jwstoken.serialize()
    return signature_data


def validate_content_length(content: any, max_size: int):
    """Validate that content does not exceed a specified maximum size"""
    if content:
        import sys
        import json

        content_length = len(json.dumps(content).encode('utf-8'))
        if content_length > max_size:
            raise ValueError(
                f"Content has length of {content_length} bytes which exceeds maximum size of {max_size} bytes"
            )


def base36_decode_with_prefix(encoded_str):
    # Strip the custom 'k' prefix before decoding, if it exists
    if encoded_str.startswith('k'):
        encoded_str = encoded_str[1:]

    # Decode using the multibase base36 decoder
    decoded_bytes = base36.decode(encoded_str)

    # Convert the bytes to a list (if necessary)
    return decoded_bytes

def get_iso_timestamp():
    return datetime.now(timezone.utc).isoformat()[:-3] + "Z"
