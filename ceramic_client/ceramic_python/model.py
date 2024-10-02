import json
import os
from typing import Any, Dict, List, Optional, Union
from base64 import urlsafe_b64encode, b64encode
from .ceramic_client import CeramicClient
from .did import DID, create_digest, encode_cid
from .helper import validate_content_length, base36_decode_with_prefix
from multiformats import CID, multihash, multicodec
import hashlib
import dag_cbor
from .stream import StreamID
from cacao.src.block import Block

DEFAULT_LOAD_OPTS = {"sync": 1}  # SyncOptions.PREFER_CACHE

MODEL_VERSION_REGEXP = r'^[0-9]+\.[0-9]+$'

DAG_CBOR_CODEC_CODE = 113
SHA2_256_CODE = 18

def parse_model_version(version: str) -> List[int]:
    import re
    if not re.match(MODEL_VERSION_REGEXP, version):
        raise ValueError(f"Unsupported version format: {version}")
    return [int(part) for part in version.split('.')]

class ModelMetadataArgs:
    def __init__(self, controller: str):
        self.controller = controller

class ModelMetadata:
    def __init__(self, controller: str, model: str):
        self.controller = controller
        self.model = model

class Model:
    STREAM_TYPE_NAME = "model"
    STREAM_TYPE_ID = 2
    VERSION = "2.0"

    @classmethod
    def MODEL(cls) -> StreamID:
        encoded_bytes = dag_cbor.encode(data="model-v1")
        # SHA256 hash
        hashed = create_digest( bytearray.fromhex(hashlib.sha256(encoded_bytes).hexdigest()) )
        cid = CID(base="base32", version=1, codec=DAG_CBOR_CODEC_CODE, digest=hashed)
        return StreamID("UNLOADABLE", cid)

    def __init__(
        self,
        ceramic_client: CeramicClient,
        content: Dict[str, Any],
        metadata: ModelMetadata,
        state: Optional[Dict[str, Any]] = None,
        stream_id: Optional[str] = None,
    ):
        super().__init__(ceramic_client, content, metadata, state, stream_id)
        self._is_read_only = False

    @property
    def content(self) -> Dict[str, Any]:
        return self._content

    @property
    def metadata(self) -> ModelMetadata:
        return ModelMetadata(
            controller=self.state.get("metadata", {}).get("controllers", [""])[0],
            model=self.MODEL(),
        )

    @classmethod
    def create(
        cls,
        ceramic_client: CeramicClient,
        content: Dict[str, Any],
        metadata: Optional[ModelMetadataArgs] = None,
    ):
        cls.assert_version_valid(content, "minor")
        cls.assert_complete(content)

        opts = {
            "publish": True,
            "anchor": True,
            "sync": 0,  # SyncOptions.NEVER_SYNC
        }

        commit = cls._make_genesis(ceramic_client.did, content, metadata)
        stream_id = ceramic_client.create_stream_from_genesis(cls.STREAM_TYPE_ID, commit, opts)
        state = ceramic_client.get_stream_state(stream_id)

        metadata_obj = ModelMetadata(
            controller=metadata.controller if metadata else ceramic_client.did.id,
            model=cls.MODEL(),
        )

        return cls(
            ceramic_client=ceramic_client,
            content=content,
            metadata=metadata_obj,
            state=state,
            stream_id=stream_id,
        )

    @staticmethod
    def assert_complete(content: Dict[str, Any], stream_id: Optional[str] = None):
        # Here you would implement the logic to check if all required fields are present
        # This is a placeholder and should be replaced with actual validation logic
        required_fields = ["name", "version"]
        for field in required_fields:
            if field not in content:
                raise ValueError(f"Missing required field: {field}")

    @staticmethod
    def assert_version_valid(content: Dict[str, Any], satisfies: str = "minor"):
        if "version" not in content:
            raise ValueError(f"Missing version for model {content.get('name', 'unknown')}")

        expected_major, expected_minor = parse_model_version(Model.VERSION)
        major, minor = parse_model_version(content["version"])

        if major > expected_major or (satisfies == "minor" and major == expected_major and minor > expected_minor):
            raise ValueError(
                f"Unsupported version {content['version']} for model {content.get('name', 'unknown')}, "
                f"the maximum version supported by the Ceramic node is {Model.VERSION}. "
                f"Please update your Ceramic node to a newer version supporting at least version {content['version']} "
                f"of the Model definition."
            )

    @staticmethod
    def assert_relations_valid(content: Dict[str, Any]):
        # Here you would implement the logic to validate relations
        # This is a placeholder and should be replaced with actual validation logic
        if "relations" in content:
            # Implement validation for relations
            pass

    @classmethod
    def load(
        cls,
        ceramic_client: CeramicClient,
        stream_id: Union[str, str, str],
        opts: Optional[Dict[str, Any]] = None,
    ):
        if opts is None:
            opts = DEFAULT_LOAD_OPTS.copy()
        else:
            opts = {**DEFAULT_LOAD_OPTS, **opts}

        stream_ref = StreamRef.from_string(str(stream_id))
        if stream_ref.type != cls.STREAM_TYPE_ID:
            raise ValueError(
                f"StreamID {stream_ref} does not refer to a '{cls.STREAM_TYPE_NAME}' stream, "
                f"but to a {stream_ref.type_name}"
            )

        state = ceramic_client.load_stream(stream_ref, opts)
        content = state.get("content", {})
        metadata = ModelMetadata(
            controller=state.get("metadata", {}).get("controllers", [""])[0],
            model=cls.MODEL(),
        )

        return cls(
            ceramic_client=ceramic_client,
            content=content,
            metadata=metadata,
            state=state,
            stream_id=str(stream_id),
        )

    @staticmethod
    def _make_genesis(
        signer: DID,
        content: Dict[str, Any],
        metadata: Optional[ModelMetadataArgs] = None,
    ):
        if content is None:
            raise ValueError("Genesis content cannot be null")

        if metadata is None:
            metadata = ModelMetadataArgs(controller=signer.id)
        elif not metadata.controller:
            metadata.controller = signer.id

        header = {
            "controllers": [metadata.controller],
            "model": Model.MODEL().bytes,
            "sep": "model",
        }

        commit = {"data": content, "header": header}
        return signer.create_dag_jws(commit)

    def make_read_only(self):
        self._is_read_only = True

    @property
    def is_read_only(self):
        return self._is_read_only

# Additional helper functions

def load_interface_implements(ceramic_client: CeramicClient, model_id: str) -> List[str]:
    model = Model.load(ceramic_client, model_id)
    if model.content.get("version") == "1.0" or not model.content.get("interface"):
        raise ValueError(f"Model {model_id} is not an interface")
    return model.content.get("implements", [])

async def load_all_model_interfaces(
    ceramic_client: CeramicClient,
    interfaces: List[str],
    loading: Dict[str, List[str]] = None,
) -> List[str]:
    if loading is None:
        loading = {}

    async def load_and_recurse(model_id):
        if model_id not in loading:
            own_implements = load_interface_implements(ceramic_client, model_id)
            sub_implements = await load_all_model_interfaces(ceramic_client, own_implements, loading)
            loading[model_id] = own_implements + sub_implements
        return loading[model_id]

    loaded = await asyncio.gather(*[load_and_recurse(model_id) for model_id in interfaces])
    return list(set(interfaces + [item for sublist in loaded for item in sublist]))