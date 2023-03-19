import json

from core.domain.entity import CardData


class ChipDecryptor:
    def __init__(self):
        pass

    def decrypt(self, encrypted_info: str) -> CardData:
        # For sake of simplicity: encrypted info is just json string
        data = json.loads(encrypted_info)
        return CardData.from_dict(data)
