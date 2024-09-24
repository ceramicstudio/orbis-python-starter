from .siwx import SiwxMessage, PERSONAL_SIGNATURE


class SiwsMessage(SiwxMessage):

    def to_message(self) -> str:
        return super().to_message('Solana')

    def sign_message(self) -> bytes:
        return self.to_message().encode('utf-8')
