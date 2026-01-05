from reedsolo import RSCodec

rsc = RSCodec(10)  # 10 parity shards

def encode(data: bytes) -> bytes:
    """Encode data with Reed-Solomon erasure coding"""
    return rsc.encode(data)

def decode(shards: list) -> bytes:
    """Decode data from shards, requires at least k shards"""
    return rsc.decode(shards)[0]