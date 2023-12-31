import asyncio
import logging
import os
from datetime import date, timedelta

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram import Bot
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, Message, message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.db.api.init_tables import run_tables
from src.db.api.utils import get_user_tg_id, get_unfilled
from src.dispatcher import get_dispatcher
from src.handlers import commands
from src.utils.get_work_keyboard import get_keyboard
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    scheduler = AsyncIOScheduler()
    commands_for_bot = []
    for cmd in commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    bot = Bot(token=os.getenv('TOKEN'))
    dp = get_dispatcher(storage=MemoryStorage())

    await bot.set_my_commands(commands=commands_for_bot)
    await run_tables()

    @dp.message(Command('send_unfilled_date'))
    async def auto_check_unfilled(message: Message):
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        user_tg_id = await get_user_tg_id()

        for tg_id in user_tg_id:
            unfilled = await get_unfilled(tg_id[0], str(start_date), str(end_date))
            if unfilled[0] is not None:
                try:
                    await bot.send_message(chat_id=tg_id[0],
                                           text=f"У тебя есть незакрытые смены за период c {start_date} по {end_date}\n"
                                                f"Выбери смену из списка ниже и отредактируй время окончания работы",
                                           reply_markup=get_keyboard(unfilled))
                except TelegramBadRequest:
                    logging.error(f"Target [ID:{tg_id[0]}]: invalid user ID")
                except TelegramRetryAfter as e:
                    logging.error(
                        f"Target [ID:{tg_id[0]}]: Flood limit is exceeded. "
                        f"Sleep {e.retry_after} seconds."
                    )
                    await asyncio.sleep(e.retry_after)
                else:
                    logging.info(f"Target [ID:{tg_id[0]}]: success")

    scheduler.add_job(auto_check_unfilled, 'cron', day_of_week='mon', hour=9, args=(message,))
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
