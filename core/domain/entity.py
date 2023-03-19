# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta
from typing import Dict, Any


class CardData(object):
    card_number: str
    name: str
    expiration_date: str
    service_code: str
    card_verification_code: str

    def __init__(self, card_number: str, name: str, expiration_date: str, service_code: str, card_verification_code: str) -> None:
        self.card_number = card_number
        self.name = name
        self.expiration_date = expiration_date
        self.service_code = service_code
        self.card_verification_code = card_verification_code

    @classmethod
    def from_dict(cls, card_dict: Dict[str, Any]) -> 'CardData':
        return cls(
            card_number=card_dict['card_number'],
            name=card_dict['name'],
            expiration_date=card_dict['expiration_date'],
            service_code=card_dict['service_code'],
            card_verification_code=card_dict['card_verification_code'],
        )

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            card_number=self.card_number,
            name=self.name,
            expiration_date=self.expiration_date,
            service_code=self.service_code,
            card_verification_code=self.card_verification_code,
        )


class Session(object):
    def __init__(self, session_id: str, card_data: CardData, ttl: int, auth_token: str = None) -> None:
        self.session_id = session_id
        self.card_data = card_data
        self.auth_token = auth_token
        self.expiry = int((datetime.now() + timedelta(minutes=ttl)).timestamp())


    # @classmethod
    # def from_dict(cls, session_dict: Dict[str, Any]) -> 'Session':
    #     return cls(
    #         session_id=session_dict['session_id'],
    #         session_data=session_dict['session_data'],
    #     )
    #
    # def to_dict(self) -> Dict[str, Any]:
    #     return dict(
    #         session_id=self.session_id,
    #         session_data=self.session_data,
    #     )
    #