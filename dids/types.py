from dataclasses import dataclass
from typing import TypedDict, Union, Dict, Optional, List, Any

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


def did_authenticate(params: AuthParams) -> GeneralJWS:
    pass


def create_jws(params: CreateJWSParams) -> Dict[str, Any]:
    pass


def decrypt_jwe(params: DecryptJWEParams) -> str:
    pass
