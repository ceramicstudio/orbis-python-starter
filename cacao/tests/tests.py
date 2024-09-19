import unittest

from src.cacao import Cacao
from src.siwe import SiweMessage


class TestCacao(unittest.TestCase):

    def test_conversion_siwe(self):
        siwe_message = SiweMessage(
            {
                "domain": "service.org",
                "address": "0x1b9Aceb609a62bae0c0a9682A9268138Faff4F5f",
                "statement": "I accept the ServiceOrg Terms of Service: https://service.org/tos",
                "uri": "did:key:z6MkrBdNdwUPnXDVD1DCxedzVVBpaGi8aSmoXFAeKNgtAer8",
                "version": "1",
                "nonce": "32891757",
                "issuedAt": "2021-09-30T16:25:24.000Z",
                "chainId": "1",
                "resources": [
                    "fs://Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu",
                    "https://example.com/my-web2-claim.json",
                    "ceramic://k2t6wyfsu4pg040dpjpbla1ybxof65baldb7fvmeam4m3n71q0w1nslz609u2d",
                ]
            }
        )

        cacao_object = Cacao()
        cacao_object.from_siwe_message(siwe_message)
        siwe_message_convert = cacao_object.to_siwe_message()
        self.assertEqual(siwe_message_convert, siwe_message)
