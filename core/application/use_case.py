# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import datetime
import logging
from typing import Optional

from core.application.errors import CardValidationError
from core.domain.entity import CardData, Session
from core.dto import ValidateCardRes, AuthRes, GetBalanceRes, DepositRes, WithdrawRes
from core.repo.bank_repo import FakeBankRepository
from core.repo.session_repo import InMemorySessionRepository
from core.util import ChipDecryptor

logger = logging.getLogger(__name__)


class ATMUseCase(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self, session_repo=InMemorySessionRepository()):
        self.session_repo = session_repo
        self.chip_decryptor = ChipDecryptor()
        self.bank_repo = FakeBankRepository()  # can substitute with real bank repo (e.g. by environment - test, prod)
        self.cash_bin = FakeCashBinUseCase()

    # validate_card handles the "Insert Card" operation. It marks the beginning of the interaction and creates a
    # session for the user.
    def validate_card(self, encrypted_card_info: str) -> ValidateCardRes:
        card_data: CardData = self.chip_decryptor.decrypt(encrypted_card_info)

        try:
            # basic card validation
            if len(card_data.card_number) != 16:
                raise CardValidationError("card number must be 16 digits")

            now = datetime.datetime.now()
            if card_data.expiration_date <= now.strftime("%Y%m%d"):
                print(now.strftime("%Y%m%d"))
                print(card_data.expiration_date)
                raise CardValidationError(f"card is expired: {card_data.expiration_date}")

            if len(card_data.card_verification_code) != 3:
                raise CardValidationError("card verification code must be 3 digits")
        except CardValidationError as e:
            return ValidateCardRes(success=False, message=str(e))

        # card data is valid, create a session
        session_id = self.session_repo.create(card_data=card_data)

        return ValidateCardRes(success=True, session_id=session_id, message="card is valid")

    # auth is responsible for authentication of "PIN Number" and account. In case of successful authentication with
    # the bank, it updates the session with auth_key AND returns account ids associated with the card for user's use
    def auth(self, pin: str, session_id: str) -> AuthRes:
        session = self.session_repo.get_if_valid(session_id=session_id)
        if not session:
            return AuthRes(success=False, message="session is invalid")

        auth_key = self.bank_repo.get_auth_key(card_data=session.card_data, pin=pin)
        if not auth_key:
            return AuthRes(success=False, message="invalid pin and auth data")

        # update session with auth_key info
        session.auth_key = auth_key
        self.session_repo.save(session=session)

        res = self.bank_repo.get_accounts(auth_key=auth_key)
        return AuthRes(success=res.success, message=res.message, account_ids=res.account_ids)

    # get_balance handles the "Select Account" and "See Balance" operation
    def get_balance(self, account_id: str, session_id: str) -> GetBalanceRes:
        session = self.session_repo.get_if_valid(session_id=session_id)
        if not session or not session.auth_key:
            return GetBalanceRes(success=False, account_id=account_id, message="session is invalid")

        res = self.bank_repo.get_balance(account_id=account_id, auth_key=session.auth_key)
        return GetBalanceRes(success=res.success, message=res.message, account_id=res.account_id, balance=res.balance)

    def deposit(self, account_id: str, session_id: str, amount: int) -> DepositRes:
        session = self.session_repo.get_if_valid(session_id=session_id)
        if not session or not session.auth_key:  # TODO: move session validation to middleware (decorator pattern)
            res = self.bank_repo.get_balance(account_id=account_id, auth_key=session.auth_key if session else "")
            return DepositRes(success=False, balance=res.balance, account_id=account_id, message="session is invalid")

        if amount > self.cash_bin.get_max_deposit():
            res = self.bank_repo.get_balance(account_id=account_id, auth_key=session.auth_key)  # TODO: reduce redundancy
            return DepositRes(success=False, balance=res.balance, account_id=account_id, message="not enough capacity in ATM")

        res = self.bank_repo.deposit(account_id=account_id, auth_key=session.auth_key, amount=amount)

        if res.success:
            self.cash_bin.add(amount=amount)

        return DepositRes(success=res.success, message=res.message, account_id=res.account_id, balance=res.balance)

    def withdraw(self, account_id: str, session_id: str, amount: int) -> WithdrawRes:
        session = self.session_repo.get_if_valid(session_id=session_id)
        if not session or not session.auth_key:
            res = self.bank_repo.get_balance(account_id=account_id, auth_key=session.auth_key if session else "")
            return WithdrawRes(success=False, balance=res.balance, account_id=account_id, message="session is invalid")

        if amount > self.cash_bin.get_total():
            res = self.bank_repo.get_balance(account_id=account_id, auth_key=session.auth_key)  # todo: reduce redundancy
            return WithdrawRes(success=False, balance=res.balance, account_id=account_id, message="not enough cash in ATM")

        res = self.bank_repo.withdraw(account_id=account_id, auth_key=session.auth_key, amount=amount)
        if res.success:
            self.cash_bin.remove(amount=amount)

        return WithdrawRes(success=res.success, message=res.message, account_id=res.account_id, balance=res.balance)



# TODO: move to different file
class AbstactCashBinUseCase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_total(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_max_deposit(self) -> int:
        raise NotImplementedError


    @abc.abstractmethod
    def add(self, amount: int) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, amount: int) -> int:
        raise NotImplementedError


class FakeCashBinUseCase(AbstactCashBinUseCase):
    def __init__(self, init_amount: int = 1000000) -> None:
        self._total = init_amount
        self._capacity = init_amount * 2

    def get_total(self) -> int:
        return self._total

    def get_max_deposit(self) -> int:
        return self._capacity - self._total

    def add(self, amount: int) -> int:
        self._total += amount
        return self._total

    def remove(self, amount: int) -> int:
        self._total -= amount
        return self._total
