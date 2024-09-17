from dataclasses import dataclass
from typing import List, Optional, Any
from multiformats import CID


@dataclass
class JWSSignature:
    protected: str
    signature: str


@dataclass
class GeneralJWS:
    payload: str
    signatures: List[JWSSignature]


@dataclass
class DagJWS:
    payload: str
    signatures: List[JWSSignature]
    link: Optional[CID] = None
