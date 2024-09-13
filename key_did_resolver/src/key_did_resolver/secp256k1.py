from multiformats import multibase

async def key_to_did_doc(pub_key_bytes: bytes, fingerprint: str) -> dict:
    did = f"did:key:{fingerprint}"
    key_id = f"{did}#{fingerprint}"
    return {
        'id': did,
        'verificationMethod': [{
            'id': key_id,
            'type': 'Secp256k1VerificationKey2018',
            'controller': did,
            'publicKeyBase58': multibase.encode(pub_key_bytes, 'base58btc'),
        }],
        'authentication': [key_id],
        'assertionMethod': [key_id],
        'capabilityDelegation': [key_id],
        'capabilityInvocation': [key_id],
    }