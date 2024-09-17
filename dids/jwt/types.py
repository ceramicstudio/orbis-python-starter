from dataclasses import dataclass
from typing import Optional, List


@dataclass
class EphemeralPublicKey:
    kty: Optional[str] = None
    crv: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    n: Optional[str] = None
    e: Optional[str] = None


@dataclass
class EphemeralKeyPair:
    publicKeyJWK: EphemeralPublicKey
    secretKey: bytes


@dataclass
class RecipientHeader:
    alg: Optional[str] = None
    iv: Optional[str] = None
    tag: Optional[str] = None
    epk: Optional[EphemeralPublicKey] = None
    kid: Optional[str] = None
    apv: Optional[str] = None
    apu: Optional[str] = None


@dataclass
class Recipient:
    header: RecipientHeader
    encrypted_key: str


@dataclass
class JWE:
    protected: str
    iv: str
    ciphertext: str
    tag: str
    aad: Optional[str] = None
    recipients: Optional[List[Recipient]] = None


@dataclass
class EncryptionResult:
    ciphertext: bytes
    tag: Optional[bytes] = None
    iv: Optional[bytes] = None
    protectedHeader: Optional[str] = None
    recipient: Optional[Recipient] = None
    cek: Optional[bytes] = None