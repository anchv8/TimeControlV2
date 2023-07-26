""" This file contains build dispatcher logic """
from typing import Optional

from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from handlers import routers
from src.utils.get_work_keyboard import kb_router


def get_dispatcher(
        storage: BaseStorage = MemoryStorage(),
        fsm_strategy: Optional[FSMStrategy] = FSMStrategy.CHAT,
        event_isolation: Optional[BaseEventIsolation] = None,
):
    """This function set up dispatcher with routers, filters and middlewares"""
    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )
    for router in routers:
        dp.include_router(router)

    dp.include_router(kb_router)
    return dp
