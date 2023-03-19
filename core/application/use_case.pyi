# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from typing import Optional, Dict

from core.domain.entity import Session
from core.dto import ValidateCardRes, AuthRes, GetBalanceRes
from core.repo.bank_repo import AbstractBankRepository
from core.repo.session_repo import AbstractSessionRepository
from core.util import ChipDecryptor


class ATMUseCase(object):
    _instance: Optional[ATMUseCase]
    chip_decryptor: ChipDecryptor
    session_repo: AbstractSessionRepository
    bank_repo: AbstractBankRepository
    # cash_bin_usecase: CashBinUseCase
    # builder: Builder

    @classmethod
    def get_instance(cls) -> ATMUseCase: ...
    def __init__(self) -> None: ...
    def validate_card(self, encrypted_card_info: str) -> ValidateCardRes: ...
    def auth(self, pin: str, session_id: str) -> AuthRes: ...
    def get_balance(self, account_id: str, session_id: str) -> GetBalanceRes: ...

    # def deposit(self, account_id: str, session_id: str, amount: int) -> DepositRes: ...
    # def withdraw(self, account_id: str, session_id: str, amount: int) -> WithdrawRes: ...


# class CashBinUseCase(object):
#     def __init__(self) -> None: ...
#     def get_total(self) -> int: ...
#     def withdraw(self, amount: int) -> bool: ...
#     def deposit(self, amount: int) -> bool: ...

