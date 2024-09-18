from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Any, List, Dict, Literal

import cbor2
from multiformats import CID

from siwx.siwe import SiweMessage
from siwx.siws import SiwsMessage
from siwx.siwTezos import SiwTezosMessage
from siwx.siwStacks import SiwStacksMessage


CLOCK_SKEW_DEFAULT_SEC = 5 * 60
LEGACY_CHAIN_ID_REORG_DATE = int(datetime(2022, 9, 20).timestamp() * 1000)


class Block:
    @staticmethod
    def decode(bytes_data: bytes, codec='dag-cbor') -> 'Block':
        if codec == 'dag-cbor':
            decoded_value = cbor2.loads(bytes_data)
        else:
            raise ValueError(f"Unsupported codec: {codec}")

        return Block(value=decoded_value)

    def __init__(self, value):
        self.value = value


@dataclass
class CacaoPayload:
    domain: str
    iss: str
    aud: str
    version: str
    nonce: str
    iat: str
    nbf: Optional[str] = None
    exp: Optional[str] = None
    statement: Optional[str] = None
    requestId: Optional[str] = None
    resources: Optional[List[str]] = None


@dataclass
class CacaoSignature:
    t: Literal['eip191', 'eip1271', 'solana:ed25519', 'tezos:ed25519', 'stacks:secp256k1', 'webauthn:p256']
    s: str
    m: Optional[Any] = None


@dataclass
class CacaoHeader:
    t: Literal['eip4361', 'caip122']


@dataclass
class Cacao:
    h: CacaoHeader
    p: CacaoPayload
    s: Optional[CacaoSignature] = None

    def from_siwe_message(self, siwe_message: SiweMessage):
        self.h.t = "eip4361"
        self.p.domain = siwe_message.domain
        self.p.iat = siwe_message.issuedAt
        self.p.iss = f'did:pkh:eip155:{siwe_message.chainId}:{siwe_message.address}'
        self.p.aud = siwe_message.uri
        self.p.version = siwe_message.version
        self.p.nonce = siwe_message.nonce

        if siwe_message.signature:
            self.s.t = "eip191"
            self.s.s = siwe_message.signature
        if siwe_message.notBefore:
            self.p.nbf = siwe_message.notBefore
        if siwe_message.expirationTime:
            self.p.exp = siwe_message.expirationTime
        if siwe_message.statement:
            self.p.statement = siwe_message.statement
        if siwe_message.requestId:
            self.p.requestId = siwe_message.requestId
        if siwe_message.resources:
            self.p.resources = siwe_message.resources

    def from_siws_message(self, siws_message: SiwsMessage):
        self.h.t = "caip122"
        self.p.domain = siws_message.domain
        self.p.iat = siws_message.issuedAt
        self.p.iss = f'did:pkh:solana:{siws_message.chainId}:{siws_message.address}'
        self.p.aud = siws_message.uri
        self.p.version = siws_message.version
        self.p.nonce = siws_message.nonce

        if siws_message.signature:
            self.s.t = "solana:ed25519"
            self.s.s = siws_message.signature
        if siws_message.notBefore:
            self.p.nbf = siws_message.notBefore
        if siws_message.expirationTime:
            self.p.exp = siws_message.expirationTime
        if siws_message.statement:
            self.p.statement = siws_message.statement
        if siws_message.requestId:
            self.p.requestId = siws_message.requestId
        if siws_message.resources:
            self.p.resources = siws_message.resources

    def from_siw_tezos_message(self, siw_tezos_message: SiwTezosMessage):
        self.h.t = "caip122"
        self.p.domain = siw_tezos_message.domain
        self.p.iat = siw_tezos_message.issuedAt
        self.p.iss = f'did:pkh:tezos:{siw_tezos_message.chainId}:${siw_tezos_message.address}'
        self.p.aud = siw_tezos_message.uri
        self.p.version = siw_tezos_message.version
        self.p.nonce = siw_tezos_message.nonce

        if siw_tezos_message.signature:
            self.s.t = "tezos:ed25519"
            self.s.s = siw_tezos_message.signature
        if siw_tezos_message.notBefore:
            self.p.nbf = siw_tezos_message.notBefore
        if siw_tezos_message.expirationTime:
            self.p.exp = siw_tezos_message.expirationTime
        if siw_tezos_message.statement:
            self.p.statement = siw_tezos_message.statement
        if siw_tezos_message.requestId:
            self.p.requestId = siw_tezos_message.requestId
        if siw_tezos_message.resources:
            self.p.resources = siw_tezos_message.resources

    def from_siw_stacks_message(self, siw_stacks_message: SiwStacksMessage):
        self.h.t = "caip122"
        self.p.domain = siw_stacks_message.domain
        self.p.iat = siw_stacks_message.issuedAt
        self.p.iss = f'did:pkh:stacks:{siw_stacks_message.chainId}:{siw_stacks_message.address}'
        self.p.aud = siw_stacks_message.uri
        self.p.version = siw_stacks_message.version
        self.p.nonce = siw_stacks_message.nonce

        if siw_stacks_message.signature:
            self.s.t = "stacks:secp256k1"
            self.s.s = siw_stacks_message.signature
        if siw_stacks_message.notBefore:
            self.p.nbf = siw_stacks_message.notBefore
        if siw_stacks_message.expirationTime:
            self.p.exp = siw_stacks_message.expirationTime
        if siw_stacks_message.statement:
            self.p.statement = siw_stacks_message.statement
        if siw_stacks_message.requestId:
            self.p.requestId = siw_stacks_message.requestId
        if siw_stacks_message.resources:
            self.p.resources = siw_stacks_message.resources

    def from_block_bytes(self, bytes_data: bytes):
        block = Block.decode(bytes_data, codec='dag-cbor')
        block_data = block.value
        if 'h' in block_data:
            self.h = CacaoHeader(**block_data['h'])
        if 'p' in block_data:
            self.p = CacaoPayload(**block_data['p'])
        if 's' in block_data:
            self.s = CacaoSignature(**block_data['s']) if block_data['s'] else None

    def verify(self, options: 'VerifyOptions'):
        if not self.s:
            raise ValueError("CACAO does not have a signature")

        if not options.verifiers[self.s.t]:
            raise ValueError("Unsupported CACAO signature type, register the needed verifier")


@dataclass
class CacaoBlock:
    value: Cacao
    cid: CID
    bytes: bytes


@dataclass
class Payload:
    domain: str
    iss: str
    aud: str
    version: str
    nonce: str
    iat: str
    nbf: Optional[str] = None
    exp: Optional[str] = None
    statement: Optional[str] = None
    requestId: Optional[str] = None
    resources: Optional[List[str]] = None


@dataclass
class VerifyOptions:
    verifiers: Dict[str, Cacao]
    atTime: Optional[datetime] = None
    revocationPhaseOutSecs: Optional[int] = None
    clockSkewSecs: Optional[int] = None
    disableExpirationCheck: Optional[bool] = None


@dataclass
class AuthMethodOpts:
    domain: Optional[str] = None
    address: Optional[str] = None
    statement: Optional[str] = None
    uri: Optional[str] = None
    version: Optional[str] = None
    nonce: Optional[str] = None
    issuedAt: Optional[str] = None
    expirationTime: Optional[str] = None
    notBefore: Optional[str] = None
    requestId: Optional[str] = None
    chainId: Optional[str] = None
    resources: Optional[List[str]] = None
