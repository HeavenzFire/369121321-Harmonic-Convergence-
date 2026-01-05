import json
from .cid import cid
from .erasure import encode

class CulturalPayload:
    def __init__(self, data: bytes, content_type: str, creator: str = "anonymous",
                 language: str = "any", shards: int = 20, required: int = 10):
        self.data = data
        self.content_id = cid(data)
        self.encoded_shards = encode(data)
        self.metadata = {
            "cid": self.content_id,
            "type": content_type,
            "license": "gift",
            "creator": creator,
            "language": language,
            "shards": shards,
            "required": required
        }

    def to_json(self) -> str:
        """Serialize payload metadata to JSON"""
        return json.dumps(self.metadata, indent=2)

    def get_shards(self) -> list:
        """Get encoded shards for distribution"""
        return [self.encoded_shards[i:i+1] for i in range(len(self.encoded_shards))]