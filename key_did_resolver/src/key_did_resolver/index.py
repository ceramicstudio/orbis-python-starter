import base58 
import math

from typing import Dict, Any, TypedDict
from . import secp256k1, ed25519, secp256r1, secp384r1, secp521r1

DID_LD_JSON = 'application/did+ld+json'
DID_JSON = 'application/did+json'

# supported drivers
prefix_to_driver_map = {
    0xe7: secp256k1,
    0xed: ed25519,
    0x1200: secp256r1,
    0x1201: secp384r1,
    0x1202: secp521r1,
}

class DIDResolutionResult(TypedDict):
    didResolutionMetadata: Dict[str, Any]
    didDocument: Dict[str, Any] | None
    didDocumentMetadata: Dict[str, Any]

class DIDResolutionOptions(TypedDict):
    accept: str | None

class ParsedDID(TypedDict):
    id: str


def base58btc_decode(string):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    alphabet_map = {char: index for index, char in enumerate(alphabet)}
    base = len(alphabet)
    
    if string.startswith('z'):
        string = string[1:]
    
    zero_count = len(string) - len(string.lstrip('1'))
    num = 0
    
    for char in string:
        num = num * base + alphabet_map[char]
    
    bytes_data = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
    return b'\x00' * zero_count + bytes_data.lstrip(b'\x00')


def decode_varint(buf, offset=0):
    MSB = 0x80
    REST = 0x7F
    res = 0
    shift = 0
    counter = offset
    length = len(buf)

    while True:
        if counter >= length or shift > 49:
            raise ValueError('Could not decode varint')

        b = buf[counter]
        counter += 1

        if shift < 28:
            res += (b & REST) << shift
        else:
            res += (b & REST) * (2 ** shift)

        shift += 7

        if b < MSB:
            break

    return res, counter - offset


def get_resolver() -> Dict[str, Any]:
    return {
        'key': resolve_key
    }

async def resolve_key(did: str, parsed: ParsedDID, resolver: Any, options: DIDResolutionOptions) -> DIDResolutionResult:
    content_type = options.get('accept', DID_JSON)
    response: DIDResolutionResult = {
        'didResolutionMetadata': {'contentType': content_type},
        'didDocument': None,
        'didDocumentMetadata': {},
    }
    
    try:
        
        multicodec_pub_key = base58btc_decode(parsed['id'])
        
        key_type, bytes_read = decode_varint(multicodec_pub_key)
        
        pub_key_bytes = multicodec_pub_key[bytes_read:]

        doc = await prefix_to_driver_map[key_type].key_to_did_doc(pub_key_bytes, parsed['id'])
        
        if content_type == DID_LD_JSON:
            doc['@context'] = 'https://w3id.org/did/v1'
            response['didDocument'] = doc
        elif content_type == DID_JSON:
            response['didDocument'] = doc
        else:
            del response['didResolutionMetadata']['contentType']
            response['didResolutionMetadata']['error'] = 'representationNotSupported'
    except Exception as e:
        response['didResolutionMetadata']['error'] = 'invalidDid'
        response['didResolutionMetadata']['message'] = str(e)
    
    return response