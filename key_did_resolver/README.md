# Key DID Resolver

This is a Python implementation of the [did:key method resolver](https://w3c-ccg.github.io/did-method-key/).

## Installation

```bash
pip install key-did-resolver
```

## Usage

```python
from key_did_resolver import get_resolver
from did_resolver import Resolver

key_did_resolver = get_resolver()
did_resolver = Resolver(key_did_resolver)

doc = await did_resolver.resolve('did:key:z6MktvqCyLxTsXUH1tUZncNdVeEZ7hNh7npPRbUU27GTrYb8')
print(doc)
```

## Supported Key Types

- Ed25519
- Secp256k1
- Secp256r1 (P-256)
- Secp384r1 (P-384)
- Secp521r1 (P-521)

## Testing

To run the tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.