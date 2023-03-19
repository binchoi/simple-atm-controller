# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import uuid
from typing import Optional

from django.db import transaction


import logging

from core.domain.entity import Session, CardData

logger = logging.getLogger(__name__)


class AbstractSessionRepository(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, session_id: str) -> Optional[Session]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, session: Session) -> None:
        raise NotImplementedError
    #
    # @abc.abstractmethod
    # def delete(self, unit_id):
    #     raise NotImplementedError

    @abc.abstractmethod
    def create(self, card_data: CardData) -> str:
        raise NotImplementedError


class InMemorySessionRepository(AbstractSessionRepository):
    SESSION_LIFETIME = 5

    def __init__(self):
        # can replace with redis
        self.kv_store = {}

    def create(self, card_data: CardData) -> str:
        session_id = str(uuid.uuid1())
        session = Session(session_id=session_id, card_data=card_data, ttl=self.SESSION_LIFETIME)
        self.kv_store[session_id] = session
        return session_id

    def get(self, session_id: str) -> Optional[Session]:
        return self.kv_store.get(session_id, None)

    def save(self, session: Session) -> None:
        self.kv_store[session.session_id] = session
        return
