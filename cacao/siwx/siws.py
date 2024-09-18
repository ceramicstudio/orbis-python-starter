from .siwx import SiwxMessage, PERSONAL_SIGNATURE


class SiwsMessage(SiwxMessage):

    def to_message(self) -> str:
        return super().to_message('Solana')

    def sign_message(self) -> bytes:
        message: bytes
        if self.type == PERSONAL_SIGNATURE:
            message = self.encode_message(self.to_message())
        else:
            message = self.encode_message(self.to_message())

        return message

    @staticmethod
    def encode_message(message: str) -> bytes:
        return message.encode('utf-8')
