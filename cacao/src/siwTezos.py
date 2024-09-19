import binascii

from .siwx import SiwxMessage, PERSONAL_SIGNATURE


class SiwTezosMessage(SiwxMessage):

    def to_message(self) -> str:
        return super().to_message('Tezos')

    def sign_message(self) -> str:
        if self.type == PERSONAL_SIGNATURE:
            message = self.encode_payload(self.to_message())
        else:
            message = self.encode_payload(self.to_message())

        return message

    @staticmethod
    def encode_payload(message: str) -> str:
        micheline_prefix = '05'
        string_prefix = '01'
        length_hex = format(len(message), '08x')
        message_hex = binascii.hexlify(message.encode('utf-8')).decode('utf-8')

        return micheline_prefix + string_prefix + length_hex + message_hex
