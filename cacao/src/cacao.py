from datetime import datetime, timedelta
from dataclasses import dataclass
from multiprocessing.managers import Value
from typing import Optional, Any, List, Dict, Literal

import cbor2
from multiformats import CID

from .siwe import SiweMessage
from .siws import SiwsMessage
from .siwTezos import SiwTezosMessage
from .siwStacks import SiwStacksMessage
from .siwx import PERSONAL_SIGNATURE, SiwxMessage
from .verification import Verifier

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
    message_object: Optional[SiwxMessage] = None

    def __init__(self):
        header = CacaoHeader('eip4361')
        payload = CacaoPayload(
            domain="",
            iss="",
            aud="",
            version="",
            nonce="",
            iat="",
        )
        self.h = header
        self.p = payload

    def from_siwe_message(self, siwe_message: SiweMessage):
        self.message_object = siwe_message
        self.h.t = "eip4361"
        self.p.domain = siwe_message.domain
        self.p.iat = siwe_message.issuedAt
        self.p.iss = f'did:pkh:eip155:{siwe_message.chainId}:{siwe_message.address}'
        self.p.aud = siwe_message.uri
        self.p.version = siwe_message.version
        self.p.nonce = siwe_message.nonce

        if siwe_message.signature:
            self.s = CacaoSignature(t="eip191", s=siwe_message.signature)
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

    def to_siwe_message(self) -> SiweMessage:
        chain_id, address = self.extract_account_chain_ids(self.p.iss)
        params = {
            "domain": self.p.domain,
            "address": address,
            "uri": self.p.aud,
            "version": self.p.version,
            "chainId": chain_id,
        }
        if self.p.statement:
            params["statement"] = self.p.statement
        if self.p.nonce:
            params["nonce"] = self.p.nonce
        if self.p.iat:
            params["issuedAt"] = self.p.iat
        if self.p.exp:
            params["expirationTime"] = self.p.exp
        if self.p.nbf:
            params["notBefore"] = self.p.nbf
        if self.p.requestId:
            params["requestId"] = self.p.requestId
        if self.p.resources:
            params["resources"] = self.p.resources

        if self.s:
            if self.s.s:
                params["signature"] = self.s.s
            if self.s.t == 'eip191':
                params["type"] = PERSONAL_SIGNATURE

        return SiweMessage(param=params)

    def from_siws_message(self, siws_message: SiwsMessage):
        self.message_object = siws_message
        self.h.t = "caip122"
        self.p.domain = siws_message.domain
        self.p.iat = siws_message.issuedAt
        self.p.iss = f'did:pkh:solana:{siws_message.chainId}:{siws_message.address}'
        self.p.aud = siws_message.uri
        self.p.version = siws_message.version
        self.p.nonce = siws_message.nonce

        if siws_message.signature:
            self.s = CacaoSignature(t="solana:ed25519", s=siws_message.signature)
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

    def to_siws_message(self) -> SiwsMessage:
        chain_id, address = self.extract_account_chain_ids(self.p.iss)
        params = {
            "domain": self.p.domain,
            "address": address,
            "uri": self.p.aud,
            "version": self.p.version,
            "chainId": chain_id,
        }
        if self.p.statement:
            params["statement"] = self.p.statement
        if self.p.nonce:
            params["nonce"] = self.p.nonce
        if self.p.iat:
            params["issuedAt"] = self.p.iat
        if self.p.exp:
            params["expirationTime"] = self.p.exp
        if self.p.nbf:
            params["notBefore"] = self.p.nbf
        if self.p.requestId:
            params["requestId"] = self.p.requestId
        if self.p.resources:
            params["resources"] = self.p.resources

        if self.s:
            if self.s.s:
                params["signature"] = self.s.s
            if self.s.t == 'eip191':
                params["type"] = PERSONAL_SIGNATURE

        return SiwsMessage(param=params)

    def from_siw_tezos_message(self, siw_tezos_message: SiwTezosMessage):
        self.message_object = siw_tezos_message
        self.h.t = "caip122"
        self.p.domain = siw_tezos_message.domain
        self.p.iat = siw_tezos_message.issuedAt
        self.p.iss = f'did:pkh:tezos:{siw_tezos_message.chainId}:${siw_tezos_message.address}'
        self.p.aud = siw_tezos_message.uri
        self.p.version = siw_tezos_message.version
        self.p.nonce = siw_tezos_message.nonce

        if siw_tezos_message.signature:
            self.s = CacaoSignature(t="tezos:ed25519", s=siw_tezos_message.signature)
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

    def to_siw_tezos_message(self) -> SiwTezosMessage:
        chain_id, address = self.extract_account_chain_ids(self.p.iss)
        params = {
            "domain": self.p.domain,
            "address": address,
            "uri": self.p.aud,
            "version": self.p.version,
            "chainId": chain_id,
        }
        if self.p.statement:
            params["statement"] = self.p.statement
        if self.p.nonce:
            params["nonce"] = self.p.nonce
        if self.p.iat:
            params["issuedAt"] = self.p.iat
        if self.p.exp:
            params["expirationTime"] = self.p.exp
        if self.p.nbf:
            params["notBefore"] = self.p.nbf
        if self.p.requestId:
            params["requestId"] = self.p.requestId
        if self.p.resources:
            params["resources"] = self.p.resources

        if self.s:
            if self.s.s:
                params["signature"] = self.s.s
            if self.s.t == 'eip191':
                params["type"] = PERSONAL_SIGNATURE

        return SiwTezosMessage(param=params)

    def from_siw_stacks_message(self, siw_stacks_message: SiwStacksMessage):
        self.message_object = siw_stacks_message
        self.h.t = "caip122"
        self.p.domain = siw_stacks_message.domain
        self.p.iat = siw_stacks_message.issuedAt
        self.p.iss = f'did:pkh:stacks:{siw_stacks_message.chainId}:{siw_stacks_message.address}'
        self.p.aud = siw_stacks_message.uri
        self.p.version = siw_stacks_message.version
        self.p.nonce = siw_stacks_message.nonce

        if siw_stacks_message.signature:
            self.s = CacaoSignature(t="stacks:secp256k1", s=siw_stacks_message.signature)
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

    def to_siw_stacks_message(self) -> SiwStacksMessage:
        chain_id, address = self.extract_account_chain_ids(self.p.iss)
        params = {
            "domain": self.p.domain,
            "address": address,
            "uri": self.p.aud,
            "version": self.p.version,
            "chainId": chain_id,
        }
        if self.p.statement:
            params["statement"] = self.p.statement
        if self.p.nonce:
            params["nonce"] = self.p.nonce
        if self.p.iat:
            params["issuedAt"] = self.p.iat
        if self.p.exp:
            params["expirationTime"] = self.p.exp
        if self.p.nbf:
            params["notBefore"] = self.p.nbf
        if self.p.requestId:
            params["requestId"] = self.p.requestId
        if self.p.resources:
            params["resources"] = self.p.resources

        if self.s:
            if self.s.s:
                params["signature"] = self.s.s
            if self.s.t == 'eip191':
                params["type"] = PERSONAL_SIGNATURE

        return SiwStacksMessage(param=params)

    def from_block_bytes(self, bytes_data: bytes):
        block = Block.decode(bytes_data, codec='dag-cbor')
        block_data = block.value
        if 'h' in block_data:
            self.h = CacaoHeader(**block_data['h'])
        if 'p' in block_data:
            self.p = CacaoPayload(**block_data['p'])
        if 's' in block_data:
            self.s = CacaoSignature(**block_data['s']) if block_data['s'] else None

    def verify(self, verifier: Verifier):
        if not self.s:
            raise ValueError("CACAO does not have a signature")

        if verifier.verifier_type != self.s.t:
            raise ValueError("Unsupported CACAO signature type, register the needed verifier")

        self.time_checks(verifier)

        verifier.verify(self.s.s, self.message_object, self.p.iss.split(":")[4])

    def time_checks(self, verifier):
        at_time = verifier.atTime if verifier.atTime else datetime.now()
        clock_skew = verifier.clockSkewSecs * 1000 if verifier.clockSkewSecs is not None else CLOCK_SKEW_DEFAULT_SEC * 1000
        issued_at = datetime.strptime(self.p.iat, '%Y-%m-%dT%H:%M:%SZ')
        if issued_at > at_time + timedelta(milliseconds=clock_skew):
            raise ValueError("CACAO is not valid yet")
        if self.p.nbf is not None:
            not_before = datetime.strptime(self.p.nbf, '%Y-%m-%dT%H:%M:%SZ')
            if not_before > at_time + timedelta(milliseconds=clock_skew):
                raise ValueError("CACAO is not valid yet")
        if not verifier.disableExpirationCheck and self.p.exp is not None:
            phase_out_miliseconds = verifier.revocationPhaseOutSecs * 1000 if verifier.revocationPhaseOutSecs is not None else 0
            if datetime.strptime(self.p.exp, '%Y-%m-%dT%H:%M:%SZ') + timedelta(
                    milliseconds=phase_out_miliseconds + clock_skew) < at_time:
                raise ValueError("CACAO has expired")

    def extract_account_chain_ids(self, iss: str) -> (str, str):
        split_iss = iss.split(":")
        return split_iss[3], split_iss[4]


@dataclass
class CacaoBlock:
    value: Cacao
    cid: CID
    bytes: bytes


@dataclass
class VerifyOptions:
    verifiers: Dict[str, Cacao]
    atTime: Optional[datetime] = None
    revocationPhaseOutSecs: Optional[int] = None
    clockSkewSecs: Optional[int] = None
    disableExpirationCheck: Optional[bool] = None
