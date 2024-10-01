import dag_cbor
from multiformats import multihash
from cid import make_cid


class Block:
    def __init__(self, data):
        self.data = data
        self.encoded_data = self.encode_data(self.data)
        self.cid = self.generate_cid()

    def encode_data(self, data):
        cacao_dict = data.to_encoder()
        return dag_cbor.encode(cacao_dict)

    def generate_cid(self):
        payload_hash = multihash.digest(self.encoded_data, "sha2-256")
        cid = make_cid(1, "dag-cbor", payload_hash)
        return cid.encode("base32").decode("utf-8")

    def decode_data(self):
        return dag_cbor.decode(self.encoded_data)

    def __repr__(self):
        return f"Block(data={self.data}, cid={self.cid})"
