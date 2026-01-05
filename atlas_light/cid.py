import blake3

def cid(data: bytes) -> str:
    """Generate content identifier using BLAKE3 hash"""
    return blake3.blake3(data).hexdigest()