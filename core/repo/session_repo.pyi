# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc

from typing import Dict, Optional

from core.domain.entity import CardData, Session


class AbstractSessionRepository(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def get(self, session_id: str) -> Optional[Session]: ...
    @abc.abstractmethod
    def save(self, session: Session) -> None: ...
    # @abc.abstractmethod
    # def delete(self, unit_id: int) -> None: ...
    @abc.abstractmethod
    def create(self, card_data: CardData) -> str: ...

class InMemorySessionRepository(AbstractSessionRepository):
    SESSION_LIFETIME: int
    kv_store: Dict[str, Session]

    def __init__(self) -> None: ...
    def get(self, session_id: str) -> Optional[Session]: ...
    def save(self, session: Session) -> None: ...
    def create(self, card_data: CardData) -> str: ...