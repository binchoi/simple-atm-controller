import json
import pytest

from core.application.use_case import ATMUseCase
from core.domain.entity import CardData


def test_usecase_validate_card():
    uc = ATMUseCase.get_instance()
    valid_card_data = CardData(
        card_number="1234567890123456",
        name="John Doe",
        expiration_date="20240101",
        card_verification_code="123",
        service_code="123"
    )

    encrypted_card_info = json.dumps(valid_card_data.to_dict())
    print(f"{encrypted_card_info=}")

    res = uc.validate_card(encrypted_card_info)
    print(f"{res=}")
    assert res.success
    assert type(res.session_id) == str
    assert res.message == "card is valid"


