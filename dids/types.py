from dataclasses import dataclass
from typing import TypedDict, Union, Dict, Optional, List
from abc import ABC, abstractmethod

from .codecs import GeneralJWS
from jwt.jwe import JWE


@dataclass
class CreateJWSParams(TypedDict):
    payload: Union[str, Dict[str, any]]
    protected: Optional[Dict[str, any]]
    revocable: Optional[bool]
    did: str


@dataclass
class AuthParams(TypedDict):
    paths: List[str]
    nonce: str
    aud: Optional[str]


@dataclass
class DecryptJWEParams(TypedDict):
    jwe: JWE
    did: Optional[str]


@dataclass
class DIDProviderClient(ABC):

    @abstractmethod
    def did_authenticate(self, params: AuthParams) -> GeneralJWS:
        pass

    @abstractmethod
    def did_create_jws(self, params: CreateJWSParams) -> GeneralJWS:
        pass

    @abstractmethod
    def did_decrypt_jwe(self, params: DecryptJWEParams) -> str:
        pass