# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import uuid
from datetime import datetime, timedelta
from typing import Optional, List


import logging

from core.domain.entity import Session, CardData
from core.dto import GetAccountsRes

logger = logging.getLogger(__name__)


class AbstractBankRepository(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_auth_key(self, card_data: CardData, pin: str) -> Optional[str]:
        raise NotImplementedError

    # @abc.abstractmethod
    # def save(self, config_setting):
    #     raise NotImplementedError
    #
    @abc.abstractmethod
    def get_accounts(self, auth_key: str) -> GetAccountsRes:
        raise NotImplementedError

    # @abc.abstractmethod
    # def create(self, card_data: CardData) -> str:
    #     raise NotImplementedError


class FakeBankRepository(AbstractBankRepository):
    SESSION_LIFETIME = 3

    def __init__(self):
        # can replace with redis
        self.auth_store = {}  # TODO: replace with sqlite
        self.session_store = {}
        self.account_store = {}

    def get_auth_key(self, card_data: CardData, pin: str) -> Optional[str]:
        pw = self.auth_store.get(card_data.card_number, "")
        # For sake of simplicity, validation logic simply cross-checks cvc, pin and expiration date
        if pw != f"{pin}#{card_data.card_verification_code}#{card_data.expiration_date}":
            return None

        auth_key = str(uuid.uuid1())
        expiration = int((datetime.now() + timedelta(minutes=self.SESSION_LIFETIME)).timestamp())

        self.session_store[auth_key] = (expiration, card_data.card_number)

        return auth_key

    def get_accounts(self, auth_key: str) -> GetAccountsRes:
        expiration, card_number = self.session_store.get(auth_key, (0, ""))
        if expiration < int(datetime.now().timestamp()):
            return GetAccountsRes(success=False, message="Auth key expired")

        accounts: List[Account] = self.account_store.get(card_number, [])
        return GetAccountsRes(success=True, message="Retrieved account ids", account_ids=[a.account_id for a in accounts])


class Account(object):
    account_id: str
    card_number: str
    balance: str

    def __init__(self, account_id: str, card_number: str, balance: str):
        self.account_id = account_id
        self.card_number = card_number
        self.balance = balance

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["account_id"], d["card_number"], d["balance"])

    def to_dict(self):
        return {"account_id": self.account_id, "card_number": self.card_number, "balance": self.balance}
