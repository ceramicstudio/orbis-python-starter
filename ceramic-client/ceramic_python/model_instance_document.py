# ceramic/model_instance_document.py

import json
import os
import dag_cbor
import jsonpatch
from typing import Any, Dict, List, Optional, Union
from base64 import urlsafe_b64encode,b64encode
from .ceramic_client import CeramicClient
from .did import DID
from .helper import validate_content_length, base36_decode_with_prefix


DEFAULT_CREATE_OPTS = {
    "anchor": True,
    "publish": True,
    "sync": 0,  # SyncOptions.NEVER_SYNC
    "syncTimeoutSeconds": 0,
}

DEFAULT_DETERMINISTIC_OPTS = {
    "anchor": False,
    "publish": False,
    "sync": 1,  # SyncOptions.PREFER_CACHE
}

DEFAULT_LOAD_OPTS = {"sync": 1}  # SyncOptions.PREFER_CACHE

DEFAULT_UPDATE_OPTS = {"anchor": True, "publish": True}


class ModelInstanceDocumentMetadataArgs:
    def __init__(
        self,
        controller: str,
        model: Any,
        context: Optional[str] = None,
        deterministic: Optional[bool] = False,
        shouldIndex: Optional[bool] = None,
    ):
        self.controller = controller
        self.model = model
        self.context = context
        self.deterministic = deterministic
        self.shouldIndex = shouldIndex


class ModelInstanceDocumentMetadata:
    def __init__(
        self,
        controller: str,
        model: Any,
        unique: Optional[bytes] = None,
        context: Optional[str] = None,
        shouldIndex: Optional[bool] = None,
    ):
        self.controller = controller
        self.model = model
        self.unique = unique
        self.context = context
        self.shouldIndex = shouldIndex


class ModelInstanceDocument:
    STREAM_TYPE_NAME = "MID"
    STREAM_TYPE_ID = 3
    MAX_DOCUMENT_SIZE = 16_000_000

    def __init__(
        self,
        ceramic_client: CeramicClient,
        content: Optional[Dict[str, Any]] = None,
        metadata: Optional[ModelInstanceDocumentMetadata] = None,
        state: Optional[Dict[str, Any]] = None,
        stream_id: Optional[str] = None,
    ):
        self.ceramic_client = ceramic_client
        self.content = content
        self.metadata = metadata
        self.state = state
        self.stream_id = stream_id
        self._is_read_only = False

    @classmethod
    def create(
        cls,
        ceramic_client: CeramicClient,
        content: Optional[Dict[str, Any]],
        metadata_args: ModelInstanceDocumentMetadataArgs,
        opts: Optional[Dict[str, Any]] = None,
    ):
        

        if opts is None:
            opts = DEFAULT_CREATE_OPTS.copy()
        else:
            opts = {**DEFAULT_CREATE_OPTS, **opts}

        signer = ceramic_client.did

        commit = cls.make_genesis(signer, content, metadata_args)
        stream_id = ceramic_client.create_stream_from_genesis(
            cls.STREAM_TYPE_ID, commit, opts
        )
        state = ceramic_client.get_stream_state(stream_id)
        
        metadata = ModelInstanceDocumentMetadata(
            controller=metadata_args.controller or signer.id,
            model=metadata_args.model,
            unique=commit.get("header", {}).get("unique"),
            context=metadata_args.context,
            shouldIndex=metadata_args.shouldIndex,
        )
        
        content = state.get("content")
        return cls(
            ceramic_client=ceramic_client,
            content=content,
            metadata=metadata,
            state=state,
            stream_id=stream_id,
        )

    @classmethod
    def load(
        cls,
        ceramic_client: CeramicClient,
        stream_id: str,
        opts: Optional[Dict[str, Any]] = None,
    ):
        if opts is None:
            opts = DEFAULT_LOAD_OPTS.copy()
        else:
            opts = {**DEFAULT_LOAD_OPTS, **opts}

        stream = ceramic_client.load_stream(stream_id, opts)
        state = stream.get("state")
        content = state.get("content")
        metadata_state = state.get("metadata", {})
        metadata = ModelInstanceDocumentMetadata(
            controller=metadata_state.get("controllers", [None])[0],
            model=metadata_state.get("model"),
            unique=metadata_state.get("unique"),
            context=metadata_state.get("context"),
            shouldIndex=metadata_state.get("shouldIndex"),
        )
        return cls(
            ceramic_client=ceramic_client,
            content=content,
            metadata=metadata,
            state=state,
            stream_id=stream_id,
        )

    def replace(
        self,
        new_content: Dict[str, Any],
        metadata_args: Optional[ModelInstanceDocumentMetadataArgs] = None,
        opts: Optional[Dict[str, Any]] = None,
    ):
        if self._is_read_only:
            self._throw_read_only_error()

        if opts is None:
            opts = DEFAULT_UPDATE_OPTS.copy()
        else:
            opts = {**DEFAULT_UPDATE_OPTS, **opts}

        validate_content_length(new_content, self.MAX_DOCUMENT_SIZE)

        signer = self.ceramic_client.did

        header = {}
        if metadata_args and metadata_args.shouldIndex is not None:
            header["shouldIndex"] = metadata_args.shouldIndex

        commit = self.make_update_commit(
            signer, self.stream_id, self.content, new_content, header
        )

        self.ceramic_client.apply_commit(self.stream_id, commit, opts)
        self.content = new_content
        self.state = self.ceramic_client.get_stream_state(self.stream_id)
        return self

    def patch(
        self,
        json_patch: List[Dict[str, Any]],
        metadata_args: Optional[ModelInstanceDocumentMetadataArgs] = None,
        opts: Optional[Dict[str, Any]] = None,
    ):
        if self._is_read_only:
            self._throw_read_only_error()

        if opts is None:
            opts = DEFAULT_UPDATE_OPTS.copy()
        else:
            opts = {**DEFAULT_UPDATE_OPTS, **opts}

        signer = self.ceramic_client.did

        for op in json_patch:
            if op["op"] in ["add", "replace"]:
                validate_content_length(op.get("value"), self.MAX_DOCUMENT_SIZE)

        raw_commit = {
            "data": json_patch,
            "prev": self.state.get("log")[-1].get("cid"),
            "id": self.stream_id,
        }

        if metadata_args and metadata_args.shouldIndex is not None:
            raw_commit["header"] = {"shouldIndex": metadata_args.shouldIndex}
            
        commit = signer.create_dag_jws(raw_commit)
        self.ceramic_client.apply_commit(self.stream_id, commit, opts)
        patched_content = jsonpatch.apply_patch(self.content, json_patch)
        self.content = patched_content
        self.state = self.ceramic_client.get_stream_state(self.stream_id)

    def should_index(self, should_index: bool, opts: Optional[Dict[str, Any]] = None):
        self.patch([], ModelInstanceDocumentMetadataArgs(None, None, shouldIndex=should_index), opts)

    def make_read_only(self):
        self._is_read_only = True

    @property
    def is_read_only(self):
        return self._is_read_only

    def _throw_read_only_error(self):
        raise Exception(
            "Historical stream commits cannot be modified. Load the stream without specifying a commit to make updates."
        )

    @staticmethod
    def make_genesis(
        signer: DID,
        content: Optional[Dict[str, Any]],
        metadata_args: ModelInstanceDocumentMetadataArgs,
        unique: Optional[List[str]] = None,
    ):
        commit = ModelInstanceDocument._make_raw_genesis(
            signer, content, metadata_args, unique
        )

        if metadata_args.deterministic:
            # No signature needed for deterministic genesis commits (which cannot have content)
            return commit
        else:
            signed_commit = signer.create_dag_jws(commit)
            return signed_commit

    @staticmethod
    def _make_raw_genesis(
        signer: DID,
        content: Optional[Dict[str, Any]],
        metadata_args: ModelInstanceDocumentMetadataArgs,
        unique: Optional[List[str]] = None,
    ):
        if not metadata_args.model:
            raise ValueError(
                "Must specify a 'model' when creating a ModelInstanceDocument"
            )

        validate_content_length(content, ModelInstanceDocument.MAX_DOCUMENT_SIZE)

        controller = metadata_args.controller or signer.as_controller()
        header = {
            "controllers": [controller],  # Remove the extra list encapsulation
            "sep": "model",
            "model": bytes(bytearray(list(base36_decode_with_prefix(metadata_args.model)))),
        }

        if metadata_args.deterministic:
            if unique:
                header["unique"] = "|".join(unique).encode("utf-8")
        else:
            random_bytes = os.urandom(12)
            header["unique"] = b64encode(random_bytes).decode('utf-8')

        if metadata_args.context:
            header["context"] = metadata_args.context

        
        return {"data": content, "header": header}

    @staticmethod
    def make_update_commit(
        signer: DID,
        stream_id: str,
        old_content: Optional[Dict[str, Any]],
        new_content: Optional[Dict[str, Any]],
        header: Optional[Dict[str, Any]] = None,
    ):
        patch = jsonpatch.make_patch(old_content or {}, new_content or {}).patch

        raw_commit = {
            "data": patch,
            "prev": None,  # Should be set to the current tip CID
            "id": stream_id,
        }

        if header:
            raw_commit["header"] = header

        signed_commit = signer.create_dag_jws(raw_commit)
        return signed_commit
