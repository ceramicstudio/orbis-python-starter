from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class ParameterSpec:
    name: str
    regex: str


@dataclass
class IdentifierSpec(ParameterSpec):
    parameters: Dict[str, Union[str, Dict[str, ParameterSpec]]]


@dataclass
class ChainIdParams:
    namespace: str
    reference: str


class ChainId:
    spec: IdentifierSpec = IdentifierSpec(
        name="ChainId",
        regex="^.*:.*$",
        parameters={
            "delimiter": ":",
            "values": {
                "namespace": ParameterSpec(name="namespace", regex=".*"),
                "reference": ParameterSpec(name="reference", regex=".*")
            }
        }
    )

    def __init__(self, params: Union[ChainIdParams, str]):
        if isinstance(params, str):
            parsed = self.parse(params)
            self.namespace = parsed.namespace
            self.reference = parsed.reference
        elif isinstance(params, ChainIdParams):
            self.namespace = params.namespace
            self.reference = params.reference

    @staticmethod
    def parse(id: str) -> ChainIdParams:
        namespace, reference = id.split(":")
        return ChainIdParams(namespace=namespace, reference=reference)

    @staticmethod
    def format(params: ChainIdParams) -> str:
        return f"{params.namespace}:{params.reference}"

    def __str__(self) -> str:
        return self.format(ChainIdParams(namespace=self.namespace, reference=self.reference))

    def to_json(self) -> ChainIdParams:
        return ChainIdParams(namespace=self.namespace, reference=self.reference)


@dataclass
class AccountIdParams:
    chainId: Union[str, ChainIdParams]
    address: str


class AccountId:
    spec: IdentifierSpec = IdentifierSpec(
        name="AccountId",
        regex="^.*:.*$",
        parameters={
            "delimiter": ":",
            "values": {
                "chainId": ParameterSpec(name="chainId", regex=".*"),
                "address": ParameterSpec(name="address", regex=".*")
            }
        }
    )

    def __init__(self, params: Union[AccountIdParams, str]):
        if isinstance(params, str):
            parsed = self.parse(params)
            self.chainId = ChainId(parsed.chainId) if isinstance(parsed.chainId, str) else ChainId(parsed.chainId)
            self.address = parsed.address
        elif isinstance(params, AccountIdParams):
            self.chainId = ChainId(params.chainId) if isinstance(params.chainId, str) else ChainId(params.chainId)
            self.address = params.address

    @staticmethod
    def parse(id: str) -> AccountIdParams:
        chain_id, address = id.split(":")
        return AccountIdParams(chainId=ChainId.parse(chain_id), address=address)

    @staticmethod
    def format(params: AccountIdParams) -> str:
        chain_id_str = ChainId.format(params.chainId) if isinstance(params.chainId, ChainIdParams) else params.chainId
        return f"{chain_id_str}:{params.address}"

    def __str__(self) -> str:
        return self.format(AccountIdParams(chainId=self.chainId.to_json(), address=self.address))

    def to_json(self) -> AccountIdParams:
        return AccountIdParams(chainId=self.chainId.to_json(), address=self.address)
