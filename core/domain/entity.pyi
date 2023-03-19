# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from typing import Dict, Any


class CardData(object):
    card_number: str
    name: str
    expiration_date: str
    service_code: str
    card_verification_code: str

    def __init__(self, card_number: str, name: str, expiration_date: str, service_code: str, card_verification_code: str) -> None:
        ...
    @classmethod
    def from_dict(cls, card_dict: Dict[str, Any]) -> CardData: ...
    def to_dict(self) -> Dict[str, Any]: ...


class Session(object):
    session_id: str
    card_data: CardData
    auth_token: str
    expiry: int

    def __init__(self, session_id: str, card_data: CardData, ttl: int, auth_token: str = None) -> None:
        ...
