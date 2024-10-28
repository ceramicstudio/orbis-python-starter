# In src/did_provider/provider.py

import json
import time
from typing import Dict, Any
from jwcrypto import jwk, jwe, jws
from jwcrypto.common import json_encode
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives import serialization
from .utils import encode_did, create_jwk, to_general_jws
from .exceptions import Ed25519ProviderError

class Ed25519Provider:
    def __init__(self, seed: bytes):
        self.ed25519_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
        self.ed25519_public_key = self.ed25519_private_key.public_key()
        self.did = encode_did(self.ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ))
        self.ed25519_jwk = create_jwk(self.ed25519_private_key)
        
        # Create X25519 key for JWE operations
        self.x25519_private_key = x25519.X25519PrivateKey.from_private_bytes(seed[:32])
        self.x25519_public_key = self.x25519_private_key.public_key()
        self.x25519_jwk = jwk.JWK.from_pem(
            self.x25519_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    async def did_authenticate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "did": self.did,
            "aud": params["aud"],
            "nonce": params["nonce"],
            "paths": params["paths"],
            "exp": int(time.time()) + 600  # expires 10 min from now
        }
        jws_token = jws.JWS(json_encode(payload))
        jws_token.add_signature(self.ed25519_jwk, protected=json_encode({"alg": "EdDSA"}))
        return to_general_jws(jws_token.serialize(compact=True))

    async def did_create_jws(self, params: Dict[str, Any]) -> Dict[str, Any]:
        request_did = params["did"].split('#')[0]
        if request_did != self.did:
            raise Ed25519ProviderError(f"Unknown DID: {params['did']}")
        jws_token = jws.JWS(json_encode(params["payload"]))
        protected = json_encode({**params.get("protected", {}), "alg": "EdDSA"})
        jws_token.add_signature(self.ed25519_jwk, protected=protected)
        return {"jws": to_general_jws(jws_token.serialize(compact=True))}

    async def did_create_jwe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        jwe_token = jwe.JWE(
            json_encode(params["payload"]),
            protected=json_encode({
                "alg": "ECDH-ES+A256KW",
                "enc": "A256GCM",
                **params.get("protected", {})
            })
        )
        jwe_token.add_recipient(self.x25519_jwk)
        return {"jwe": jwe_token.serialize()}

    async def did_decrypt_jwe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        jwe_token = jwe.JWE()
        jwe_token.deserialize(params["jwe"])
        jwe_token.decrypt(self.x25519_jwk)
        return {"cleartext": json.loads(jwe_token.payload)}

    async def send(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        method = msg["method"]
        params = msg["params"]
        
        if method == "did_authenticate":
            return await self.did_authenticate(params)
        elif method == "did_createJWS":
            return await self.did_create_jws(params)
        elif method == "did_createJWE":
            return await self.did_create_jwe(params)
        elif method == "did_decryptJWE":
            return await self.did_decrypt_jwe(params)
        else:
            raise Ed25519ProviderError(f"Unknown method: {method}")
        


# src/key_did_provider_ed25519/provider.py
