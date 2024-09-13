# key-did-provider-ed25519

A TypeScript library for managing Decentralized Identifiers (DIDs) using the `did:key` method with Ed25519 keys. It implements EIP2844 and supports decryption using X25519.

## Features

- DID creation and management using Ed25519 keys
- JSON Web Signature (JWS) creation and verification
- JSON Web Encryption (JWE) creation and decryption
- Authentication using DIDs

## Installation```bash
npm install --save key-did-provider-ed25519
```

## Usage

Here's a basic example of how to use the Ed25519Provider:

```python
import asyncio
from did_provider import DIDProvider

async def main():
    seed = b'0' * 32  # replace with the actual seed
    provider = DIDProvider(seed)
    
    # Authenticate
    auth_result = await provider.send({
        "method": "did_authenticate",
        "params": {
            "aud": "https://example.com",
            "nonce": "1234567890",
            "paths": ["/protected/resource"]
        }
    })
    
    print("Authentication result:", auth_result)

# Run the main function
asyncio.run(main())

```

For more examples, see the `examples` directory.

## Testing

To run the tests:

```bash
python -m unittest discover tests
```

## License

This project is licensed under the MIT License.

