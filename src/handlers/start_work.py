import logging

import asyncpg
from aiogram import types, Router, exceptions
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from src.db.api.start_work import set_start_work
from src.db.api.utils import is_start_time_set
from src.middlewares.is_register import IsRegister
from src.states import DateTimeStates

start_work_router = Router(name='start_work')
start_work_router.message.middleware(IsRegister())


# Команда записи времени начала работы
@start_work_router.message(Command('startwork'))
@start_work_router.message(Text(text='⏳ Начало работы'))
async def start_work(message: types.Message, state: FSMContext):
    logging.info(f"User [id={message.from_user.id}] used command [command={message.text}]")
    await state.clear()
    if not await is_start_time_set(message.from_user.id, message.date.strftime("%Y-%m-%d")):
        await message.answer("Введи время начала работы в формате ЧЧ:ММ")
        await state.set_state(DateTimeStates.START_TIME)
    else:
        await message.answer("Время начала работы за сегодня уже записано!")


# Обработка сообщения о начале работы
@start_work_router.message(DateTimeStates.START_TIME)
async def process_start_work(message: types.Message, state: FSMContext):
    try:
        hours, minutes = map(int, message.text.split(":"))
        if (0 <= hours <= 24) and (0 <= minutes <= 60):
            await state.update_data(start_time=message.text)
            data = await state.get_data()
            await state.set_data(data)
            start_time = data.get('start_time')
            await set_start_work(message.from_user.id, message.date.strftime("%Y-%m-%d"),
                                 start_time)
            await message.answer("Работа начата! Не забудь поставить отметку об окончании работы командой /endwork")
            await state.clear()
        else:
            await message.answer("Некорректно введено время! Попробуй снова")
    except (exceptions, asyncpg.exceptions) as e:
        await message.answer(f"Непредвиденная ошибка: {e}")
