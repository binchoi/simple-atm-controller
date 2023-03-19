# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import uuid
from datetime import datetime, timedelta
from typing import Optional, List


import logging

from core.domain.entity import Session, CardData
from core.dto import GetAccountsRes, GetBankBalanceRes, BankDepositRes, BankWithdrawRes

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

    @abc.abstractmethod
    def get_balance(self, auth_key: str, account_id: str) -> GetBankBalanceRes:
        raise NotImplementedError

    @abc.abstractmethod
    def deposit(self, auth_key: str, account_id: str, amount: int) -> BankDepositRes:
        raise NotImplementedError

    @abc.abstractmethod
    def withdraw(self, auth_key: str, account_id: str, amount: int) -> BankWithdrawRes:
        raise NotImplementedError


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

    def get_balance(self, auth_key: str, account_id: str) -> GetBankBalanceRes:
        expiration, card_number = self.session_store.get(auth_key, (0, ""))
        if expiration < int(datetime.now().timestamp()):
            return GetBankBalanceRes(success=False, account_id=account_id, message="Auth key expired")

        accounts: List[Account] = self.account_store.get(card_number, [])
        # TODO: use better storage solution as this is O(n) - suboptimal performance
        for a in accounts:
            if a.account_id == account_id:
                return GetBankBalanceRes(
                    success=True,
                    message="Retrieved account balance",
                    account_id=account_id,
                    balance=a.balance
                )

        return GetBankBalanceRes(success=False, account_id=account_id, message="Account not found")

    def deposit(self, auth_key: str, account_id: str, amount: int) -> BankDepositRes:
        # TODO: move the session_store logic to middleware / annotation-based (cross-cutting concern)
        expiration, card_number = self.session_store.get(auth_key, (0, ""))
        if expiration < int(datetime.now().timestamp()):
            return BankDepositRes(success=False, account_id=account_id, message="Auth key expired")

        accounts: List[Account] = self.account_store.get(card_number, [])
        for a in accounts:
            if a.account_id == account_id:
                a.balance += amount
                # later when in DB, remember to commit

                return BankDepositRes(
                    success=True,
                    message="Deposit successful",
                    account_id=account_id,
                    balance=a.balance
                )
        return BankDepositRes(success=False, account_id=account_id, message="Account not found")

    def withdraw(self, auth_key: str, account_id: str, amount: int) -> BankWithdrawRes:
        expiration, card_number = self.session_store.get(auth_key, (0, ""))
        if expiration < int(datetime.now().timestamp()):
            return BankWithdrawRes(success=False, account_id=account_id, message="Auth key expired")

        accounts: List[Account] = self.account_store.get(card_number, [])
        for a in accounts:
            if a.account_id == account_id:
                if a.balance < amount:
                    return BankWithdrawRes(
                        success=False,
                        message="Insufficient balance",
                        account_id=account_id,
                        balance=a.balance
                    )

                a.balance -= amount
                # later when in DB, remember to commit

                return BankWithdrawRes(
                    success=True,
                    message="Withdraw successful",
                    account_id=account_id,
                    balance=a.balance
                )
        return BankWithdrawRes(success=False, account_id=account_id, message="Account not found")


class Account(object):
    account_id: str
    card_number: str
    balance: int

    def __init__(self, account_id: str, card_number: str, balance: int):
        self.account_id = account_id
        self.card_number = card_number
        self.balance = balance

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["account_id"], d["card_number"], d["balance"])

    def to_dict(self):
        return {"account_id": self.account_id, "card_number": self.card_number, "balance": self.balance}
