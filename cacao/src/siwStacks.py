from .siwx import SiwxMessage, PERSONAL_SIGNATURE

class SiwStacksMessage(SiwxMessage):

    def to_message(self) -> str:
        return super().to_message('Stacks')

    def sign_message(self) -> str:
        if self.type == PERSONAL_SIGNATURE:
            message = self.to_message()
        else:
            message = self.to_message()

        return message