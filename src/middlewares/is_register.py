from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.db.api.utils import is_exist


class IsRegister(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        check = await is_exist(event.from_user.id)
        if check:
            return await handler(event, data)

        await event.answer(
            "Вижу, что тебя нет в списках! Зарегистрируйся с помощью команды /start .",
            show_alert=True
        )
        return
