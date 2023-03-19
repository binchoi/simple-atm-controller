import json
import pytest

from core.application.use_case import ATMUseCase
from core.domain.entity import CardData, Session
from core.dto import GetAccountsRes, GetBankBalanceRes, BankDepositRes, BankWithdrawRes


# TODO: add assert_called_with checks for each test

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


def test_usecase_auth_success(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    # TODO: include assert called with checks
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.get_auth_key",
        return_value="11111"
    )

    mock_response = GetAccountsRes(success=True, message="Retrieved account ids", account_ids=["7777"])
    mocker.patch("core.repo.bank_repo.FakeBankRepository.get_accounts", return_value=mock_response)

    uc = ATMUseCase.get_instance()
    res = uc.auth(pin="1234", session_id="1234")

    assert res.success
    assert res.message == mock_response.message
    assert res.account_ids == mock_response.account_ids


def test_usecase_auth_failure(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    # TODO: include assert called with checks
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.get_auth_key",
        return_value="11111"
    )

    mock_response = GetAccountsRes(success=False, message="Invalid PIN", account_ids=[])
    mocker.patch("core.repo.bank_repo.FakeBankRepository.get_accounts", return_value=mock_response)

    # When
    uc = ATMUseCase.get_instance()
    res = uc.auth(pin="1234", session_id="1234")

    # Then
    assert not res.success
    assert res.message == mock_response.message
    assert res.account_ids == mock_response.account_ids


def test_usecase_get_balance_success(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    # TODO: include assert called with checks
    mock_bank_res = GetBankBalanceRes(success=True, message="Retrieved balance", account_id="101010", balance=100000)
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.get_balance",
        return_value=mock_bank_res
    )

    uc = ATMUseCase.get_instance()
    res = uc.get_balance(account_id="101010", session_id="1234")

    assert res.success
    assert res.message == mock_bank_res.message
    assert res.account_id == mock_bank_res.account_id
    assert res.balance == mock_bank_res.balance


def test_usecase_get_balance_failure_when_session_invalid(mocker):
    # Given
    mock_sessions = [
        Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key=None  # No Auth Key
        ),
        None,  # Invalid Session / Expired
        ]
    for s in mock_sessions:
        mocker.patch(
            "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
            return_value=s
        )

        uc = ATMUseCase.get_instance()
        res = uc.get_balance(account_id="101010", session_id="1234")

        assert not res.success
        assert res.account_id == "101010"
        assert res.message == "session is invalid"
        assert res.balance is None


def test_usecase_get_balance_failure_due_to_bank(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )
    mock_bank_res_possibilities = [
        GetBankBalanceRes(success=False, account_id="101010", message="Auth key expired"),
        GetBankBalanceRes(success=False, account_id="101010", message="Account not found"),
    ]

    for r in mock_bank_res_possibilities:
        mocker.patch(
            "core.repo.bank_repo.FakeBankRepository.get_balance",
            return_value=r
        )

        uc = ATMUseCase.get_instance()
        res = uc.get_balance(account_id="101010", session_id="1234")

        assert not res.success
        assert res.message == r.message
        assert res.account_id == r.account_id
        assert res.balance == r.balance


def test_usecase_deposit_success(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    # TODO: include assert called with checks
    mock_bank_res = BankDepositRes(success=True, message="Deposit successful", account_id="101010", balance=100)
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.deposit",
        return_value=mock_bank_res
    )

    uc = ATMUseCase.get_instance()
    res = uc.deposit(account_id="101010", session_id="1234", amount=10)

    assert res.success
    assert res.message == mock_bank_res.message
    assert res.account_id == mock_bank_res.account_id
    assert res.balance == mock_bank_res.balance
    assert uc.cash_bin.get_total() == 1000010 # cash bin is updated


def test_usecase_deposit_failure_due_to_capacity(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    mock_bank_res = GetBankBalanceRes(success=True, message="Retrieved balance", account_id="101010", balance=123)
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.get_balance",
        return_value=mock_bank_res
    )

    uc = ATMUseCase.get_instance()
    res = uc.deposit(account_id="101010", session_id="1234", amount=1000000000000)

    assert not res.success
    assert res.message == "not enough capacity in ATM"
    assert res.account_id == "101010"
    assert res.balance == 123  # Unchanged


def test_usecase_deposit_failure_due_to_session(mocker):
    mock_sessions = [
        Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key=None  # No Auth Key
        ),
        None,  # Invalid Session / Expired
        ]
    for s in mock_sessions:
        mocker.patch(
            "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
            return_value=s
        )

        mock_bank_res = GetBankBalanceRes(success=True, message="Retrieved balance", account_id="101010", balance=123)
        mocker.patch(
            "core.repo.bank_repo.FakeBankRepository.get_balance",
            return_value=mock_bank_res
        )

        uc = ATMUseCase.get_instance()
        res = uc.deposit(account_id="101010", session_id="1234", amount=1234)

        assert not res.success
        assert res.message == "session is invalid"
        assert res.account_id == "101010"
        assert res.balance == 123  # Unchanged


def test_usecase_withdraw_success(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    # TODO: include assert called with checks
    mock_bank_res = BankWithdrawRes(success=True, message="Withdraw successful", account_id="101010", balance=100)
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.withdraw",
        return_value=mock_bank_res
    )

    uc = ATMUseCase.get_instance()
    init_cash_bin = uc.cash_bin.get_total()
    res = uc.withdraw(account_id="101010", session_id="1234", amount=100)

    assert res.success
    assert res.message == mock_bank_res.message
    assert res.account_id == mock_bank_res.account_id
    assert res.balance == mock_bank_res.balance
    assert uc.cash_bin.get_total() == init_cash_bin-100  # cash bin is updated


def test_usecase_withdraw_failure_due_to_cashbin(mocker):
    # Given
    mock_session = Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key="11111"
        )

    mocker.patch(
        "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
        return_value=mock_session
    )

    mock_bank_res = GetBankBalanceRes(success=True, message="Retrieved balance", account_id="101010", balance=123)
    mocker.patch(
        "core.repo.bank_repo.FakeBankRepository.get_balance",
        return_value=mock_bank_res
    )

    uc = ATMUseCase.get_instance()
    res = uc.withdraw(account_id="101010", session_id="1234", amount=1000000000000)

    assert not res.success
    assert res.message == "not enough cash in ATM"
    assert res.account_id == "101010"
    assert res.balance == 123  # Unchanged


def test_usecase_withdraw_failure_due_to_session(mocker):
    mock_sessions = [
        Session(
            session_id="1234",
            card_data=CardData(
                card_number="1234567890123456",
                name="John Doe",
                expiration_date="20240101",
                card_verification_code="123",
                service_code="123"
            ),
            ttl=10,
            auth_key=None  # No Auth Key
        ),
        None,  # Invalid Session / Expired
        ]
    for s in mock_sessions:
        mocker.patch(
            "core.repo.session_repo.InMemorySessionRepository.get_if_valid",
            return_value=s
        )

        mock_bank_res = GetBankBalanceRes(success=True, message="Retrieved balance", account_id="101010", balance=123)
        mocker.patch(
            "core.repo.bank_repo.FakeBankRepository.get_balance",
            return_value=mock_bank_res
        )

        uc = ATMUseCase.get_instance()
        res = uc.withdraw(account_id="101010", session_id="1234", amount=1234)

        assert not res.success
        assert res.message == "session is invalid"
        assert res.account_id == "101010"
        assert res.balance == 123  # Unchanged




