# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging

from core.application.errors import CardValidationError
from core.domain.entity import CardData
from core.dto import ValidateCardRes, AuthRes
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

    # auth is responsible for authentication of PIN and account. In case of successful authentication with the bank,
    # it updates the session with auth_key AND returns account ids associated with the card for users to choose from
    def auth(self, pin: str, session_id: str) -> AuthRes:
        session = self.session_repo.get(session_id=session_id)
        auth_key = self.bank_repo.get_auth_key(card_data=session.card_data, pin=pin)
        if not auth_key:
            return AuthRes(success=False, message="invalid pin and auth data")

        # update session with auth_key info
        session.auth_key = auth_key
        self.session_repo.save(session=session)

        res = self.bank_repo.get_accounts(auth_key=auth_key)
        return AuthRes(success=res.success, message=res.message, account_ids=res.account_ids)


    # def get_balance(self, account_id: str, session_id: str) -> GetBalanceRes: ...
    # def deposit(self, account_id: str, session_id: str, amount: int) -> DepositRes: ...
    # def withdraw(self, account_id: str, session_id: str, amount: int) -> WithdrawRes: ...

