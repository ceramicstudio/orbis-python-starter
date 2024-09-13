# src/key_did_provider_ed25519/__init__.py

from .provider import Ed25519Provider
from .exceptions import Ed25519ProviderError

__all__ = ['Ed25519Provider', 'Ed25519ProviderError']
__version__ = '0.1.0'