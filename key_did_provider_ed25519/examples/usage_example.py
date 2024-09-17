import asyncio
from did_provider import DIDProvider

async def main():
    seed = b'0' * 32  # replace with actual seed
    provider = DIDProvider(seed)
    
    # Example authentication
    auth_params = {
        "aud": "https://example.com",
        "nonce": "1234567890",
        "paths": ["/protected/resource"]
    }
    auth_result = await provider.send({
        "method": "did_authenticate",
        "params": auth_params
    })

    
    # Example JWE creation and decryption
    jwe_params = {
        "payload": {"hello": "world"},
        "protected": {"enc": "A256GCM"}
    }
    jwe_result = await provider.send({
        "method": "did_createJWE",
        "params": jwe_params
    })
    
    decrypt_result = await provider.send({
        "method": "did_decryptJWE",
        "params": {"jwe": jwe_result["jwe"]}
    })

if __name__ == "__main__":
    asyncio.run(main())