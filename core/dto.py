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

