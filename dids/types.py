from typing import TypedDict, Union, Dict, Optional, List, Any

from .jwe import JWE
from .codecs import GeneralJWS


class CreateJWSParams(TypedDict):
    payload: Union[str, Dict[str, any]]
    protected: Optional[Dict[str, any]]
    revocable: Optional[bool]
    did: str


class AuthParams(TypedDict):
    paths: List[str]
    nonce: str
    aud: Optional[str]


class DecryptJWEParams(TypedDict):
    jwe: JWE
    did: Optional[str]


def did_authenticate(params: AuthParams) -> GeneralJWS:
    pass


def create_jws(params: CreateJWSParams) -> Dict[str, Any]:
    pass


def decrypt_jwe(params: DecryptJWEParams) -> str:
    pass
