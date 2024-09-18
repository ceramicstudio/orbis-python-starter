from web3 import Web3

from .siwx import SiwxMessage, PERSONAL_SIGNATURE


class SiweMessage(SiwxMessage):

    def to_message(self) -> str:
        return super().to_message("Ethereum")

    def to_message_eip55(self) -> str:
        address = Web3.to_checksum_address(self.address)
        return super().to_message('Ethereum', address)

    def sign_message(self, eip55: bool = False) -> str:
        if self.type == PERSONAL_SIGNATURE:
            return self.to_message_eip55() if eip55 else self.to_message()
        else:
            return self.to_message_eip55() if eip55 else self.to_message()
