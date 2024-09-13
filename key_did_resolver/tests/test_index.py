import unittest
from src.key_did_resolver import get_resolver

class TestResolver(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.resolver_registry = get_resolver()
        self.resolve = self.resolver_registry['key']

    async def test_resolves_document_from_did(self):
        parsed_did = {
            'id': "zQ3shbgnTGcgBpXPdBjDur3ATMDWhS7aPs6FRFkWR19Lb9Zwz",
            'did': 'did:key:zQ3shbgnTGcgBpXPdBjDur3ATMDWhS7aPs6FRFkWR19Lb9Zwz',
            'method': 'key',
            'didUrl': 'did:key:zQ3shbgnTGcgBpXPdBjDur3ATMDWhS7aPs6FRFkWR19Lb9Zwz/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:zQ3shbgnTGcgBpXPdBjDur3ATMDWhS7aPs6FRFkWR19Lb9Zwz', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:zQ3shbgnTGcgBpXPdBjDur3ATMDWhS7aPs6FRFkWR19Lb9Zwz', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

        # Next parsed_did
        parsed_did = {
            'id': "z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8",
            'did': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8',
            'method': 'key',
            'didUrl': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

        # Third parsed_did
        parsed_did = {
            'id': "zruuPojWkzGPb8sVc42f2YxcTXKUTpAUbdrzVovaTBmGGNyK6cGFaA4Kp7SSLKecrxYz8Sc9d77Rss7rayYt1oFCaNJ",
            'did': 'did:key:zruuPojWkzGPb8sVc42f2YxcTXKUTpAUbdrzVovaTBmGGNyK6cGFaA4Kp7SSLKecrxYz8Sc9d77Rss7rayYt1oFCaNJ',
            'method': 'key',
            'didUrl': 'did:key:zruuPojWkzGPb8sVc42f2YxcTXKUTpAUbdrzVovaTBmGGNyK6cGFaA4Kp7SSLKecrxYz8Sc9d77Rss7rayYt1oFCaNJ/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:zruuPojWkzGPb8sVc42f2YxcTXKUTpAUbdrzVovaTBmGGNyK6cGFaA4Kp7SSLKecrxYz8Sc9d77Rss7rayYt1oFCaNJ', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:zruuPojWkzGPb8sVc42f2YxcTXKUTpAUbdrzVovaTBmGGNyK6cGFaA4Kp7SSLKecrxYz8Sc9d77Rss7rayYt1oFCaNJ', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

        # Fourth parsed_did
        parsed_did = {
            'id': "zDnaeUKTWUXc1HDpGfKbEK31nKLN19yX5aunFd7VK1CUMeyJu",
            'did': 'did:key:zDnaeUKTWUXc1HDpGfKbEK31nKLN19yX5aunFd7VK1CUMeyJu',
            'method': 'key',
            'didUrl': 'did:key:zDnaeUKTWUXc1HDpGfKbEK31nKLN19yX5aunFd7VK1CUMeyJu/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:zDnaeUKTWUXc1HDpGfKbEK31nKLN19yX5aunFd7VK1CUMeyJu', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:zDnaeUKTWUXc1HDpGfKbEK31nKLN19yX5aunFd7VK1CUMeyJu', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

        # Fifth parsed_did
        parsed_did = {
            'id': "z4oJ8emo5e6mGPCUS5wncFZXAyuVzGRyJZvoduwq7FrdZYPd1LZQbDKsp1YAMX8x14zBwy3yHMSpfecJCMDeRFUgFqYsY",
            'did': 'did:key:z4oJ8emo5e6mGPCUS5wncFZXAyuVzGRyJZvoduwq7FrdZYPd1LZQbDKsp1YAMX8x14zBwy3yHMSpfecJCMDeRFUgFqYsY',
            'method': 'key',
            'didUrl': 'did:key:z4oJ8emo5e6mGPCUS5wncFZXAyuVzGRyJZvoduwq7FrdZYPd1LZQbDKsp1YAMX8x14zBwy3yHMSpfecJCMDeRFUgFqYsY/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:z4oJ8emo5e6mGPCUS5wncFZXAyuVzGRyJZvoduwq7FrdZYPd1LZQbDKsp1YAMX8x14zBwy3yHMSpfecJCMDeRFUgFqYsY', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:z4oJ8emo5e6mGPCUS5wncFZXAyuVzGRyJZvoduwq7FrdZYPd1LZQbDKsp1YAMX8x14zBwy3yHMSpfecJCMDeRFUgFqYsY', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

        # Sixth parsed_did
        parsed_did = {
            'id': "z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54",
            'did': 'did:key:z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54',
            'method': 'key',
            'didUrl': 'did:key:z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54/some/path',
            'path': '/some/path'
        }

        doc = await self.resolve('did:key:z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54', parsed_did, {}, {'accept': 'application/did+ld+json'})
        self.assertIsNotNone(doc)
        
        doc = await self.resolve('did:key:z82LkvCwHNreneWpsgPEbV3gu1C6NFJEBg4srfJ5gdxEsMGRJUz2sG9FE42shbn2xkZJh54', parsed_did, {}, {'accept': 'application/did+json'})
        self.assertIsNotNone(doc)

    async def test_throws_error_for_unsupported_did(self):
        parsed_did = {
            'id': "z6LSeu9HkTHSfLLeUs2nnzUSNedgDUevfNQgQjQC23ZCit6F",
            'did': 'did:key:z6LSeu9HkTHSfLLeUs2nnzUSNedgDUevfNQgQjQC23ZCit6F',
            'method': 'key',
            'didUrl': 'did:key:z6LSeu9HkTHSfLLeUs2nnzUSNedgDUevfNQgQjQC23ZCit6F/some/path',
            'path': '/some/path'
        }
        expectation = "TypeError: 'keyToDidDoc' is not defined"
        
        result = await self.resolve('did:key:z6LSeu9HkTHSfLLeUs2nnzUSNedgDUevfNQgQjQC23ZCit6F', parsed_did, {}, {'accept': 'application/did+ld+json'})
 
        self.assertEqual(result['didResolutionMetadata']['error'], "invalidDid")
        self.assertIsNone(result['didDocument'])

    async def test_throws_error_for_unsupported_media_type(self):
        parsed_did = {
            'id': "z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8",
            'did': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8',
            'method': 'key',
            'didUrl': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8/some/path',
            'path': '/some/path'
        }

        result = await self.resolve('did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8', parsed_did, {}, {'accept': 'application/rdf+xml'})
        self.assertEqual(result['didResolutionMetadata']['error'], 'representationNotSupported')

    async def test_defaults_to_did_json_when_no_media_type_specified(self):
        parsed_did = {
            'id': "z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8",
            'did': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8',
            'method': 'key',
            'didUrl': 'did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8/some/path',
            'path': '/some/path'
        }

        result = await self.resolve('did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8', parsed_did, {}, {})
        self.assertEqual(result['didResolutionMetadata']['contentType'], 'application/did+json')


if __name__ == '__main__':
    unittest.main()
