from dataclasses import dataclass


@dataclass
class ValidateCardRes:
    success: bool
    message: str
    session_id: str = None

#
# @dataclass
# class AuthRes:
#     pass
