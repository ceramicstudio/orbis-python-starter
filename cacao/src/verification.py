from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from eth_account.messages import encode_defunct
from eth_account import Account
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from .siwe import SiweMessage
from .siws import SiwsMessage
from .siwx import SiwxMessage


@dataclass
class Verifier(ABC):
    verifier_type: str
    atTime: Optional[datetime] = None
    revocationPhaseOutSecs: Optional[int] = None
    clockSkewSecs: Optional[int] = None
    disableExpirationCheck: bool = False

    @abstractmethod
    def verify(self, signature: str, message: SiwxMessage, address: str):
        pass


class EIP191Verifier(Verifier):

    def __init__(self):
        self.verifier_type = "eip191"

    def verify(self, signature: str, siwe_message: SiweMessage, address: str):
        message_hash = encode_defunct(text=siwe_message.to_message_eip55())
        recovered_address = Account.recover_message(message_hash, signature=signature)

        if recovered_address.lower() == address.lower():
            pass
        else:
            raise ValueError("Signature is invalid")


class SolanaVerifier(Verifier):

    def __init__(self):
        self.verifier_type = "solana:ed25519"

    def verify(self, signature: str, siws_message: SiwsMessage, address: str):
        signature = base58.b58decode(signature)
        public_key = base58.b58decode(address)
        verify_key = VerifyKey(public_key)

        try:
            verify_key.verify(siws_message.sign_message(), signature)
        except BadSignatureError:
            print("Invalid signature!")
