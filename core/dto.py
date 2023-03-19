from dataclasses import dataclass
from typing import List


@dataclass
class ValidateCardRes:
    success: bool
    message: str = None
    session_id: str = None


@dataclass
class AuthRes:
    success: bool
    message: str = None
    account_ids: List[str] = None


@dataclass
class GetAccountsRes:
    success: bool
    message: str = None
    account_ids: List[str] = None

# TODO: create a base class for below res


@dataclass
class GetBalanceRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None


@dataclass
class GetBankBalanceRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None


@dataclass
class DepositRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None


@dataclass
class BankDepositRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None


@dataclass
class WithdrawRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None


@dataclass
class BankWithdrawRes:
    success: bool
    balance: int = None
    account_id: str = None
    message: str = None
