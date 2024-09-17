from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

from did_resolver import Resolver, Resolvable

from .types import EphemeralKeyPair, EncryptionResult, Recipient


class Encrypter(ABC):

    def __init__(self, alg: str, enc: str):
        self.alg = alg
        self.enc = enc

    @abstractmethod
    def encrypt(
            self,
            cleartext: bytes,
            protected_header: Dict[str, Any],
            aad: Optional[bytes] = None,
            ephemeral_key_pair: Optional[EphemeralKeyPair] = None
    ) -> EncryptionResult:
        pass

    def encrypt_cek(self, cek: bytes, ephemeral_key_pair: Optional[EphemeralKeyPair] = None) -> Optional[Recipient]:
        return None

    def gen_epk(self) -> Optional[EphemeralKeyPair]:
        return None


class Decrypter(ABC):

    def __init__(self, alg: str, enc: str):
        self.alg = alg
        self.enc = enc

    @abstractmethod
    def decrypt(
            self,
            sealed: bytes,
            iv: bytes,
            aad: Optional[bytes] = None,
            recipient: Optional[Recipient] = None
    ) -> Optional[bytes]:
        pass
