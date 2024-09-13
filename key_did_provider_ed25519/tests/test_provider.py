
import unittest
import asyncio
from src.key_did_provider_ed25519 import Ed25519Provider, Ed25519ProviderError

class TestEd25519Provider(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.seed = b'0' * 32  # Test seed
        self.provider = Ed25519Provider(self.seed)

    async def test_did_creation(self):
        self.assertTrue(self.provider.did.startswith("did:key:z"))

    async def test_authentication(self):
        auth_params = {
            "aud": "https://example.com",
            "nonce": "1234567890",
            "paths": ["/protected/resource"]
        }
        result = await self.provider.send({
            "method": "did_authenticate",
            "params": auth_params
        })
        self.assertIn("payload", result)
        self.assertIn("signatures", result)

    async def test_jws_creation(self):
        jws_params = {
            "did": self.provider.did,
            "payload": {"hello": "world"},
            "protected": {"additional": "header"}
        }
        result = await self.provider.send({
            "method": "did_createJWS",
            "params": jws_params
        })
        self.assertIn("jws", result)
        self.assertIn("payload", result["jws"])
        self.assertIn("signatures", result["jws"])

    async def test_jwe_encryption_decryption(self):
        jwe_params = {
            "payload": {"secret": "message"},
            "protected": {"enc": "A256GCM"}
        }
        encrypt_result = await self.provider.send({
            "method": "did_createJWE",
            "params": jwe_params
        })
        self.assertIn("jwe", encrypt_result)

        decrypt_result = await self.provider.send({
            "method": "did_decryptJWE",
            "params": {"jwe": encrypt_result["jwe"]}
        })
        self.assertIn("cleartext", decrypt_result)
        self.assertEqual({"secret": "message"}, decrypt_result["cleartext"])

    async def test_unknown_method(self):
        with self.assertRaises(Ed25519ProviderError):
            await self.provider.send({
                "method": "unknown_method",
                "params": {}
            })

    async def test_invalid_did_for_jws(self):
        jws_params = {
            "did": "did:key:invalidDID",
            "payload": {"hello": "world"},
        }
        with self.assertRaises(Ed25519ProviderError):
            await self.provider.send({
                "method": "did_createJWS",
                "params": jws_params
            })

if __name__ == '__main__':
    unittest.main()    