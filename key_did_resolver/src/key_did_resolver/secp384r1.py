from multiformats import multibase
from cryptography.hazmat.primitives.asymmetric import ec

async def key_to_did_doc(pub_key_bytes: bytes, fingerprint: str) -> dict:
    did = f"did:key:{fingerprint}"
    key_id = f"{did}#{fingerprint}"
    
    public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP384R1(), pub_key_bytes)
    public_numbers = public_key.public_numbers()
    
    return {
        'id': did,
        'verificationMethod': [{
            'id': key_id,
            'type': 'JsonWebKey2020',
            'controller': did,
            'publicKeyJwk': {
                'kty': 'EC',
                'crv': 'P-384',
                'x': multibase.encode(public_numbers.x.to_bytes(48, 'big'), 'base64url'),
                'y': multibase.encode(public_numbers.y.to_bytes(48, 'big'), 'base64url'),
            },
        }],
        'authentication': [key_id],
        'assertionMethod': [key_id],
        'capabilityDelegation': [key_id],
        'capabilityInvocation': [key_id],
    }