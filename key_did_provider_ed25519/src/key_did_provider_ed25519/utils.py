import base58
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from jwcrypto import jwk
from typing import Dict, Any

def encode_did(public_key: bytes) -> str:
    multicodec_prefix = bytes([0xed, 0x01])  # ed25519 multicodec
    full_bytes = multicodec_prefix + public_key
    return f"did:key:z{base58.b58encode(full_bytes).decode()}"

def create_jwk(private_key: ed25519.Ed25519PrivateKey) -> jwk.JWK:
    return jwk.JWK.from_pem(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

def to_general_jws(jws_token: str) -> Dict[str, Any]:
    protected_header, payload, signature = jws_token.split('.')
    return {
        "payload": payload,
        "signatures": [{"protected": protected_header, "signature": signature}],
    }