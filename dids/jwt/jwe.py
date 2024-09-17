from typing import Dict, Any
import base64
import json

from .encryption import Encrypter, Decrypter
from .types import *


def bytes_to_base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def decode_base64url(data: str) -> str:
    return base64.urlsafe_b64decode(data + '==').decode('utf-8')


def string_to_bytes(data: str) -> bytes:
    return data.encode('utf-8')


def base64_to_bytes(s: str) -> bytes:
    input_base64_url = s.replace('-', '+').replace('_', '/')
    padding = '=' * ((4 - len(input_base64_url) % 4) % 4)
    return base64.urlsafe_b64decode(input_base64_url + padding)


def to_sealed(ciphertext: str, tag: Optional[str] = None) -> bytes:
    ciphertext_bytes = base64_to_bytes(ciphertext)
    tag_bytes = base64_to_bytes(tag) if tag else b''
    return ciphertext_bytes + tag_bytes


def validate_jwe(jwe: JWE) -> None:
    if not (jwe.protected and jwe.iv and jwe.ciphertext and jwe.tag):
        raise ValueError('bad_jwe: missing properties')

    if jwe.recipients:
        for rec in jwe.recipients:
            if not (rec.header and rec.encrypted_key):
                raise ValueError('bad_jwe: malformed recipients')


def encode_jwe(encryption_result: EncryptionResult, aad: Optional[bytes] = None) -> JWE:
    jwe = JWE(
        protected=encryption_result.protectedHeader or '',
        iv=bytes_to_base64url(encryption_result.iv or b''),
        ciphertext=bytes_to_base64url(encryption_result.ciphertext),
        tag=bytes_to_base64url(encryption_result.tag or b''),
    )

    if aad:
        jwe.aad = bytes_to_base64url(aad)

    if encryption_result.recipient:
        jwe.recipients = [encryption_result.recipient]

    return jwe


def create_jwe(
    cleartext: bytes,
    encrypters: List[Encrypter],
    protected_header: Dict[str, Any] = {},
    aad: Optional[bytes] = None,
    use_single_ephemeral_key: bool = False
) -> JWE:
    if encrypters[0].alg == 'dir':
        if len(encrypters) > 1:
            raise ValueError('not_supported: Can only do "dir" encryption to one key.')

        encryption_result = encrypters[0].encrypt(cleartext, protected_header, aad)
        return encode_jwe(encryption_result, aad)
    else:
        tmp_enc = encrypters[0].enc
        if not all(encrypter.enc == tmp_enc for encrypter in encrypters):
            raise ValueError('invalid_argument: Incompatible encrypters passed')

        cek: Optional[bytes] = None
        jwe: Optional[JWE] = None
        epk: Optional[EphemeralKeyPair] = None

        if use_single_ephemeral_key:
            epk = encrypters[0].gen_epk()
            alg = encrypters[0].alg
            protected_header = {**protected_header, 'alg': alg, 'epk': epk.publicKeyJWK if epk else None}

        for encrypter in encrypters:
            if cek is None:
                encryption_result: EncryptionResult = encrypter.encrypt(cleartext, protected_header, aad, epk)
                cek = encryption_result.cek
                jwe = encode_jwe(encryption_result, aad)
            else:
                recipient = encrypter.encrypt_cek(cek, epk)
                if recipient:
                    if jwe and jwe.recipients is None:
                        jwe.recipients = []
                    if jwe:
                        jwe.recipients.append(recipient)

        if jwe is None:
            raise ValueError('Encryption failed, no JWE generated')

        return jwe


def decrypt_jwe(jwe: JWE, decrypter: Decrypter) -> bytes:
    validate_jwe(jwe)
    prot_header = json.loads(decode_base64url(jwe.protected))
    if prot_header['enc'] != decrypter.enc:
        raise ValueError(f"not_supported: Decrypter does not support: '{prot_header['enc']}'")

    sealed = to_sealed(jwe.ciphertext, jwe.tag)
    aad = string_to_bytes(f"{jwe.protected}.{jwe.aad}" if jwe.aad else jwe.protected)

    cleartext: Optional[bytes] = None

    if prot_header['alg'] == 'dir' and decrypter.alg == 'dir':
        cleartext = decrypter.decrypt(sealed, base64_to_bytes(jwe.iv), aad)
    elif not jwe.recipients or len(jwe.recipients) == 0:
        raise ValueError('bad_jwe: missing recipients')
    else:
        for recipient in jwe.recipients:
            if cleartext is None:
                recipient.header = RecipientHeader(**prot_header)
                if recipient.header.alg == decrypter.alg:
                    cleartext = decrypter.decrypt(sealed, base64_to_bytes(jwe.iv), aad, recipient)

    if cleartext is None:
        raise ValueError('failure: Failed to decrypt')

    return cleartext
