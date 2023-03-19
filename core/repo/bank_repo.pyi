# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc

from typing import Dict, Optional, Tuple, List, Any

from core.domain.entity import CardData, Session
from core.dto import GetAccountsRes


class AbstractBankRepository(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def get_auth_key(self, card_data: CardData, pin: str) -> Optional[str]: ...
    @abc.abstractmethod
    def get_accounts(self, auth_key: str) -> GetAccountsRes: ...
    # @abc.abstractmethod
    # def delete(self, unit_id: int) -> None: ...
    # @abc.abstractmethod
    # def create(self, card_data: CardData) -> str: ...

class FakeBankRepository(AbstractBankRepository):
    auth_store: Dict[str, str]
    session_store: Dict[str, Tuple[int, str]]
    account_store: Dict[str, List[Account]]
    SESSION_LIFETIME: int

    def __init__(self) -> None: ...
    def get_auth_key(self, card_data: CardData, pin: str) -> Optional[str]: ...
    def get_accounts(self, auth_key: str) -> GetAccountsRes: ...
    # def create(self, card_data: CardData) -> str: ...


class Account(object):
    account_id: str
    card_number: str
    balance: str

    def __init__(self, account_id: str, card_number: str, balance: str):
        ...
    @classmethod
    def from_dict(cls, d: dict) -> Account: ...
    def to_dict(self) -> Dict[str, Any]: ...