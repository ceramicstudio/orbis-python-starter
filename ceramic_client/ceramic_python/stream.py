from multiformats import varint
from typing import Union, Dict, Any, Tuple
from functools import cached_property
from multiformats import CID, multihash
from multiformats.multibase import base36
import dag_cbor
from typing import Dict, Optional, List
import numpy as np


STREAMID_CODEC = 206

def from_bytes(input_bytes: bytes, title: str = 'StreamRef') -> Dict[str, Union[str, int, CID, None]]:

    def read_varint(bytes_: bytes) -> Tuple[int, bytes, int]:
        if not bytes_:
            raise ValueError("Input bytes are empty")

        try:
            value, read_length = varint.decode_bytes(bytes_)
            remainder = bytes_[read_length:]
            return value, remainder, read_length
        except varint.DecodeError as e:
            raise ValueError(f"Failed to decode varint: {e}")

    def is_cid_version(version: int) -> bool:
        return version in (0, 1)

    def read_cid(bytes_: bytes) -> Tuple[CID, bytes]:
        
        def read_varint(data: bytes) -> Tuple[int, bytes]:
            value, read_length = varint.decode_bytes(data)
            return value, data[read_length:]

        cid_version, cid_version_remainder = read_varint(bytes_)
        if not is_cid_version(cid_version):
            raise ValueError(f"Unknown CID version {cid_version}")

        codec, codec_remainder = read_varint(cid_version_remainder)
        mh_code, mh_code_remainder = read_varint(codec_remainder)
        mh_length, mh_length_remainder = read_varint(mh_code_remainder)

        mh_value_start = len(codec_remainder) - len(mh_length_remainder)
        mh_value_end = mh_value_start + mh_length
        multihash_bytes = codec_remainder[mh_value_start:mh_value_end]
        
        multihash_bytes_remainder = codec_remainder[mh_value_end:]

        # Reconstruct the full multihash
        full_multihash = varint.encode(mh_code) + varint.encode(mh_length) + multihash_bytes

        # Create the CID
        cid = CID.from_raw_v1(codec, multihash.decode(full_multihash))

        return cid, multihash_bytes_remainder

    stream_codec, stream_codec_remainder = read_varint(input_bytes)
    if stream_codec != STREAMID_CODEC:
        raise ValueError(f"Invalid {title}, does not include streamid codec")

    stream_type, stream_type_remainder = read_varint(stream_codec_remainder)
    genesis, genesis_remainder = read_cid(stream_type_remainder)

    if len(genesis_remainder) == 0:
        return {
            "kind": "stream-id",
            "type": stream_type,
            "genesis": genesis,
        }
    elif len(genesis_remainder) == 1 and genesis_remainder[0] == 0:
        # Zero commit
        return {
            "kind": "commit-id",
            "type": stream_type,
            "genesis": genesis,
            "commit": None,
        }
    else:
        # Commit
        commit, _ = read_cid(genesis_remainder)
        return {
            "kind": "commit-id",
            "type": stream_type,
            "genesis": genesis,
            "commit": commit,
        }

def concat(arrays: List[np.ndarray], length: Optional[int] = None) -> np.ndarray:
    """
    Concatenate a list of Uint8Arrays.

    Args:
        arrays (List[np.ndarray]): List of Uint8Arrays to concatenate.
        length (Optional[int]): Total length of the resulting array. If None, it's calculated.

    Returns:
        np.ndarray: Concatenated Uint8Array.
    """
    if length is None:
        length = sum(arr.nbytes for arr in arrays)

    output = alloc_unsafe(length)
    offset = 0

    for arr in arrays:
        output[offset:offset + arr.nbytes] = arr
        offset += arr.nbytes

    return as_uint8array(output)

def alloc_unsafe(size: int = 0) -> np.ndarray:
    """
    Allocate a new Uint8Array of the given size.

    Args:
        size (int): Size of the array to allocate.

    Returns:
        np.ndarray: A new Uint8Array.
    """
    return np.zeros(size, dtype=np.uint8)

def as_uint8array(buf: np.ndarray) -> np.ndarray:
    """
    Ensure the input is a Uint8Array.

    Args:
        buf (np.ndarray): Input array.

    Returns:
        np.ndarray: The input array as a Uint8Array.
    """
    return buf.view(np.uint8)

# Registry of stream types
registry: Dict[str, Optional[int]] = {
    "tile": 0,
    "caip10-link": 1,
    "model": 2,
    "MID": 3,
    "UNLOADABLE": 4,
}

def code_by_name(name: str) -> int:
    """
    Get the code for a given stream type name.
    
    Args:
        name (str): The name of the stream type.
    
    Returns:
        int: The code corresponding to the stream type name.
    
    Raises:
        ValueError: If no stream type is registered for the given name.
    """
    index = registry.get(name)
    if index is not None:
        return index
    else:
        raise ValueError(f"No stream type registered for name {name}")

def name_by_code(index: int) -> str:
    """
    Get the name for a given stream type code.
    
    Args:
        index (int): The code of the stream type.
    
    Returns:
        str: The name corresponding to the stream type code.
    
    Raises:
        ValueError: If no stream type is registered for the given index.
    """
    for name, code in registry.items():
        if code == index:
            return name
    raise ValueError(f"No stream type registered for index {index}")

class StreamType:
    """
    A class to represent stream types.
    """
    name_by_code = staticmethod(name_by_code)
    code_by_name = staticmethod(code_by_name)

class InvalidStreamIDBytesError(Exception):
    def __init__(self, bytes_: bytes):
        super().__init__(f"Invalid StreamID bytes {base36.encode(bytes_)}: contains commit")

class InvalidStreamIDStringError(Exception):
    def __init__(self, input_: str):
        super().__init__(f"Invalid StreamID string {input_}: contains commit")

class StreamID:
    TAG = '@ceramicnetwork/streamid/StreamID'

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> 'StreamID':
        parsed = from_bytes(bytes_, 'StreamID')
        if parsed['kind'] == 'stream-id':
            return cls(parsed['type'], parsed['genesis'])
        raise InvalidStreamIDBytesError(bytes_)


    def __init__(self, type_: Union[str, int], cid: Union[CID, str]):
        if not (type_ or type_ == 0):
            raise ValueError('StreamID constructor: type required')
        if not cid:
            raise ValueError('StreamID constructor: cid required')
        self._type = StreamType.code_by_name(type_) if isinstance(type_, str) else type_
        self._cid = CID.decode(cid) if isinstance(cid, str) else cid

    @classmethod
    async def from_genesis(cls, type_: Union[str, int], genesis: Dict[str, Any]) -> 'StreamID':
        block = await dag_cbor.encode(genesis)
        return cls(type_, block.cid)

    @property
    def type(self) -> int:
        return self._type

    @cached_property
    def type_name(self) -> str:
        return StreamType.name_by_code(self._type)

    @property
    def cid(self) -> CID:
        return self._cid

    @property
    def bytes(self) -> bytes:
        codec = varint.encode(STREAMID_CODEC)
        type_ = varint.encode(self.type)
        
        # Handle the case where cid.encode() returns a string
        cid_bytes = self.cid.encode()
        if isinstance(cid_bytes, str):
            cid_bytes = cid_bytes.encode('utf-8')
        
        return b''.join([
            codec if isinstance(codec, bytes) else bytes(codec),
            type_ if isinstance(type_, bytes) else bytes(type_),
            cid_bytes
        ])

    @cached_property
    def base_id(self) -> 'StreamID':
        return StreamID(self._type, self._cid)

    def equals(self, other: 'StreamID') -> bool:
        if isinstance(other, StreamID):
            return self.type == other.type and self.cid == other.cid
        return False

    @cached_property
    def to_string(self) -> str:
        return base36.encode(self.bytes)

    @cached_property
    def to_url(self) -> str:
        return f"ceramic://{self.to_string}"

    def __repr__(self) -> str:
        return f"StreamID({self.to_string})"

    def __str__(self) -> str:
        return self.to_string
