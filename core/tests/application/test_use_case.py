import json
import pytest

from core.application.use_case import ATMUseCase
from core.domain.entity import CardData


def test_usecase_validate_card_success():
    uc = ATMUseCase.get_instance()
    valid_card_datas = [
        CardData(
            card_number="1234567890123456",
            name="John Doe",
            expiration_date="20240101",
            card_verification_code="123",
            service_code="123"
        ),
        CardData(
            card_number="1234567890123986",
            name="Bob",
            expiration_date="20280101",
            card_verification_code="432",
            service_code="111"
        ),
    ]

    for valid_card_data in valid_card_datas:
        encrypted_card_info = json.dumps(valid_card_data.to_dict())
        res = uc.validate_card(encrypted_card_info)
        assert res.success
        assert type(res.session_id) == str
        assert res.message == "card is valid"


def test_usecase_validate_card_failure():
    uc = ATMUseCase.get_instance()
    invalid_card_datas = [
        (CardData(
            card_number="123456789012345678",
            name="John Doe",
            expiration_date="20240101",
            card_verification_code="123",
            service_code="123"
        ), "card number must be 16 digits"),
        (CardData(
            card_number="1234567890123986",
            name="Bob",
            expiration_date="20000101",
            card_verification_code="432",
            service_code="111"
        ), "card is expired: 20000101"),
        (CardData(
            card_number="1234567890123986",
            name="Bob",
            expiration_date="20240101",
            card_verification_code="42222",
            service_code="111"
        ), "card verification code must be 3 digits"),
    ]

    for valid_card_data, message in invalid_card_datas:
        encrypted_card_info = json.dumps(valid_card_data.to_dict())
        res = uc.validate_card(encrypted_card_info)
        assert not res.success
        assert res.session_id is None
        assert res.message == message


# TODO: add more tests (table driven) for validate_card


# def test_usecase_auth_success():



