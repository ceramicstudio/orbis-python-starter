from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from eth_account.messages import encode_defunct
from eth_account import Account

from .siwe import SiweMessage


@dataclass
class Verifier(ABC):
    verifier_type: str
    atTime: Optional[datetime] = None
    revocationPhaseOutSecs: Optional[int] = None
    clockSkewSecs: Optional[int] = None
    disableExpirationCheck: bool = False

    @abstractmethod
    def verify(self, signature: str, message: str, address: str):
        pass


class EIP191Verifier(Verifier):

    def verify(self, signature: str, siwe_message: SiweMessage, address: str):
        message_hash = encode_defunct(text=siwe_message.to_message_eip55())
        recovered_address = Account.recover_message(message_hash, signature=signature)

        if recovered_address.lower() == address.lower():
            pass
        else:
            raise ValueError("Signature is invalid")
