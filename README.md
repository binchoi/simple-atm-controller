# Simple ATM Controller

#### A simple ATM controller that allows you to check your balance, deposit money, and withdraw money from your accounts. It is written in Python 3.6+ and uses pytest for testing.

### Requirements
* Python 3.6+
* pip3

#### To install the requirements, run the following command:

    $ pip3 install -r requirements.txt


#### Running tests with pytest

    $ pytest

---
### Project Structure
Most of the work is in the `/core` module
    
        .
        └── core
            ├── application
            │   ├── errors.py   # custom exceptions
            │   ├── use_case.py # ATM Controller (i.e. ATMUseCase) and CashBin Implementation (move later)
            │   └── ... 
            ├── domain
            │   ├── entity.py   # CardData and Session entity
            │   └── ... 
            ├── migrations
            │   └── ... 
            ├── repo
            │   ├── bank_repo.py    # bank repo (i.e. AbstractBankRepository, FakeBankRepository), if real Bank API is used, it could implement AbstractBankRepository
            │   ├── session_repo.py # session repo ensures safe transactions (i.e. AbstractSessionRepository, InMemorySessionRepository) 
            │   └── ... 
            ├── tests
            │   ├── application
            │   │   ├── test_use_case.py  # ATM Controller tests (i.e. ATMUseCase) -- will contain other UseCase tests too
            │   │   └── ... 
            │   └── repo
            │       └── ... # soon to house repo-specific tests 
            ├── dto.py      # dto's such as GetAccountsRes, GetBalanceRes, DepositRes, ... used to transfer data across layers  
            └── util.py     # contains util functions/classes (i.e. ChipDecryptor)


### Design Decisions
* The ATM Controller (i.e. ATMUseCase) is the main entry point for the application. It is responsible for orchestrating the flow of the application. It is also responsible for some user input validations. It is implemented as follows:
```
class ATMUseCase(object):
    _instance: Optional[ATMUseCase]
    chip_decryptor: ChipDecryptor
    session_repo: AbstractSessionRepository
    bank_repo: AbstractBankRepository
    cash_bin: AbstactCashBinUseCase
    # builder: Builder

    @classmethod
    def get_instance(cls) -> ATMUseCase: ...  # singleton pattern
    def __init__(self) -> None: ...
    def validate_card(self, encrypted_card_info: str) -> ValidateCardRes: ...     # "insert card"
    def auth(self, pin: str, session_id: str) -> AuthRes: ...                     # "pin & display accounts"
    def get_balance(self, account_id: str, session_id: str) -> GetBalanceRes: ... 
    def deposit(self, account_id: str, session_id: str, amount: int) -> DepositRes: ...
    def withdraw(self, account_id: str, session_id: str, amount: int) -> WithdrawRes: ...

```

#### Session & Security
* A session begins when the magnetic chip of the credit card is successfully decrypted and its data validated **(use_case.py:L56)** and is valid for (by default) **5 minutes**. This is to ensure safety of transactions. The session is stored in memory (i.e. InMemorySessionRepository) and is invalidated after the session expires (TODO: implement TTL via Redis).
* In addition, when communicating with the Bank API for account information and transactions, the client first goes through an authentication process (i.e. PIN number initiated process). The auth key that is returned is used to authenticate the client for the duration of the session. This is to ensure that the client is who they say they are. The auth key is stored in the session storage and is invalidated after the session expires.
  * The Auth Key expires (by default) after **3 minutes** since issue.

#### Database & Persistence
* Due to time constraints, in-memory data-structures are used instead of a database. However, the code is structured in such a way that it is easy to swap out the in-memory data-structures for a database.
* Some databases that are suitable for the project include, **RDBMS** (including MySQL, PostgreSQL, and SQLite) for Account and User Data (for Bank-side; not within ATM domain) and NoSQL database Redis (for session stores, cashbin).
* RDBMS is preferred for Account, Balance data as RDBMS typically prioritizes strict consistency and safety of data. NoSQL databases are more suitable for session stores and cashbin as they are more available and scalable (apt for key-value queries).

#### Docker 
* Due to time constraints, Docker is not implemented. However, it is not too difficult to containerize using Docker and Docker Compose. This will simplify the setup process for the application and its dependencies (especially with multiple DBs).
