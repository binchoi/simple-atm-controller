# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging

from core.application.errors import CardValidationError
from core.domain.entity import CardData
from core.dto import ValidateCardRes
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

    # def auth(self, pin: str, session_id: str) -> AuthRes:
    #     pass

    # def get_balance(self, account_id: str, session_id: str) -> GetBalanceRes: ...
    # def deposit(self, account_id: str, session_id: str, amount: int) -> DepositRes: ...
    # def withdraw(self, account_id: str, session_id: str, amount: int) -> WithdrawRes: ...

    # def get_config_data(
    #         self,
    #         unit_id
    # ):
    #     try:
    #         config_setting = self.config_repo.get(unit_id=unit_id)
    #     except ConfigNotFound:
    #         config_setting = ConfigSetting.default_config_setting(unit_id=unit_id)
    #     except Exception as e:
    #         raise InternalError("error: {}".format(str(e)))
    #
    #     return self.builder.entity_to_config_data(config_setting=config_setting)
    #
    # def upsert_config_data(
    #         self,
    #         unit_id,
    #         contents,
    #         config_data
    # ):
    #     try:
    #         config_setting = self.builder.build_config_setting(unit_id=unit_id, contents=contents, config_data=config_data)
    #     except (InvalidConfigSetting, InvalidTab, InvalidFilter, InvalidAdConfig, InvalidRevenueCollectionType, InvalidCategory, InvalidShoppingCategory, TabsNotFound, FiltersNotFound, CategoryNotFound, ShoppingCategoryNotFound) as e:
    #         logger.error("upsert_config_data: {} \nerror: {}".format(config_data, str(e)))
    #         raise e
    #
    #     try:
    #         self.config_repo.save(config_setting=config_setting)
    #     except Exception as e:
    #         raise InternalError("config_data: {} \nerror: {}".format(config_data, str(e)))
    #
    # def delete_config(self, unit_id):
    #     try:
    #         self.config_repo.delete(unit_id=unit_id)
    #     except ConfigNotFound:
    #         return
    #     except Exception as e:
    #         raise InternalError(str(e))
    #
    # def validate_config_data(self, config_data):
    #     if config_data is None or \
    #             not all(key in config_data for key in ("auto_loading", "tabs")):
    #         raise InvalidConfigData("required parameter missing(auto_loading, tabs)")
    #
    #     tabs = config_data.get('tabs')
    #     if not isinstance(tabs, list):
    #         raise InvalidConfigData("invalid tabs")
    #
    #     for tab in tabs:
    #         if not all(key in tab for key in ("name", "ad_config")):
    #             raise InvalidConfigData("invalid tab")
    #
    #         ad_config = tab['ad_config']
    #         if not all(key in ad_config for key in ("revenue_collection_types", "categories", "shopping_categories"))\
    #                 or not isinstance(ad_config["revenue_collection_types"], list) \
    #                 or not isinstance(ad_config["categories"], list) \
    #                 or not isinstance(ad_config["shopping_categories"], list):
    #             raise InvalidConfigData("invalid ad_config")
    #
    #         if len(ad_config["revenue_collection_types"]) == 0:
    #             raise InvalidConfigData("invalid request format")
    #
    #         if RevenueCollectionType.SHOPPING.value not in ad_config["revenue_collection_types"] and len(ad_config["shopping_categories"]) > 0:
    #             raise InvalidConfigData("invalid request format")
    #
    #         disable_chips = tab.get("disable_chips", False)  # config_data that doesn't contain disable_chips considered valid (backward compatibility)
    #         if not isinstance(disable_chips, bool):
    #             raise InvalidConfigData("invalid disable_chips")
    #
    #     try:
    #         self.builder.build_config_setting(unit_id=0, contents=False, config_data=config_data)
    #     except (InvalidConfigSetting, InvalidTab, TabNotAllowed, InvalidFilter, InvalidRevenueCollectionType, InvalidCategory, InvalidShoppingCategory, TabsNotFound, FiltersNotFound, CategoryNotFound, ShoppingCategoryNotFound) as e:
    #         logger.warn("validate_config_data: {} \nerror: {}".format(config_data, str(e)))
    #         raise e
