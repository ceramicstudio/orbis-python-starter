from dataclasses import dataclass
from typing import Optional, List

from jwcrypto import jwk, jws
from jwcrypto.common import json_decode


@dataclass
class JsonWebKey:
    alg: Optional[str]
    crv: Optional[str]
    e: Optional[str]
    ext: Optional[bool]
    key_ops: Optional[List[str]]
    kid: Optional[str]
    kty: Optional[str]
    n: Optional[str]
    use: Optional[str]
    x: Optional[str]
    y: Optional[str]


@dataclass
class VerificationMethod:
    id: str
    type: str
    controller: str
    publicKeyBase58: Optional[str] = None
    publicKeyBase64: Optional[str] = None
    publicKeyJwk: Optional[JsonWebKey] = None
    publicKeyHex: Optional[str] = None
    publicKeyMultibase: Optional[str] = None
    blockchainAccountId: Optional[str] = None
    ethereumAddress: Optional[str] = None

    # ConditionalProof2022 subtypes
    conditionOr: Optional[List['VerificationMethod']] = None
    conditionAnd: Optional[List['VerificationMethod']] = None
    threshold: Optional[int] = None
    conditionThreshold: Optional[List['VerificationMethod']] = None
    conditionWeightedThreshold: Optional[List['ConditionWeightedThreshold']] = None
    conditionDelegated: Optional[str] = None
    relationshipParent: Optional[List[str]] = None
    relationshipChild: Optional[List[str]] = None
    relationshipSibling: Optional[List[str]] = None


@dataclass
class ConditionWeightedThreshold:
    weight: float
    condition: VerificationMethod


def extract_public_key_jwk(verification_method: VerificationMethod) -> jwk.JWK:
    if verification_method.publicKeyJwk:
        return jwk.JWK(**verification_method.publicKeyJwk)
    raise ValueError("Unsupported public key format or missing key information.")


def verify_jws(jws_token: str, pub_keys: List[VerificationMethod]) -> VerificationMethod:
    jws_object = jws.JWS()
    jws_object.deserialize(jws_token)

    header = json_decode(jws_object.jose_header)
    alg = header.get('alg')

    for pk in pub_keys:
        try:
            pub_key_jwk = extract_public_key_jwk(pk)
            jws_object.verify(pub_key_jwk, alg=alg)
            return pk
        except Exception as e:
            raise ValueError(e)

    raise ValueError("No valid signer found for the provided JWS token.")
