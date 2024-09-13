from multiformats import multibase
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def encode_key(key: bytes) -> str:
    bytes_with_multicodec = b'\xec\x01' + key
    return f"z{multibase.encode(bytes_with_multicodec, 'base58btc')}"

async def key_to_did_doc(pub_key_bytes: bytes, fingerprint: str) -> dict:
    did = f"did:key:{fingerprint}"
    key_id = f"{did}#{fingerprint}"
    
    # Convert Ed25519 public key to X25519
    ed25519_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)
    x25519_key = ed25519_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    x25519_key_id = f"{did}#{encode_key(x25519_key)}"
    
    return {
        'id': did,
        'verificationMethod': [{
            'id': key_id,
            'type': 'Ed25519VerificationKey2018',
            'controller': did,
            'publicKeyBase58': multibase.encode(pub_key_bytes, 'base58btc'),
        }],
        'authentication': [key_id],
        'assertionMethod': [key_id],
        'capabilityDelegation': [key_id],
        'capabilityInvocation': [key_id],
        'keyAgreement': [{
            'id': x25519_key_id,
            'type': 'X25519KeyAgreementKey2019',
            'controller': did,
            'publicKeyBase58': multibase.encode(x25519_key, 'base58btc'),
        }],
    }