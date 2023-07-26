from src.db.api.get_work import get_work_time
from src.db.api.utils import get_unfilled
from src.middlewares.is_register import IsRegister
from src.states import CustomStates
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3b8_calendar import SimpleCalCallback, SimpleCalendar

from src.utils.get_work_keyboard import get_keyboard
from src.utils.utils import calculate_total, get_week_dates, get_month_dates

get_work_router = Router()
get_work_router.message.middleware(IsRegister())


# Клавиатура с выбором периода выгрузки
@get_work_router.message(Command('getwork'))
@get_work_router.message(Text('📄 Мои смены'))
async def get_data_handler(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="Текущий месяц", callback_data="month"),
        types.InlineKeyboardButton(text="Эта неделя", callback_data="week"),
        types.InlineKeyboardButton(text="Свободный выбор", callback_data="custom")
    )
    await message.answer("Выбери период:", reply_markup=keyboard.as_markup())


# Обработчик колбэка с клавиатуры
@get_work_router.callback_query(lambda query: query.data in ["month", "week", "custom"])
async def process_time_period(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    if callback_query.data == "month":
        start_date, end_date = await get_month_dates()
    elif callback_query.data == "week":
        start_date, end_date = await get_week_dates()
    else:
        await callback_query.message.answer("Выбери начало периода: ",
                                            reply_markup=SimpleCalendar().start_calendar())
        await state.set_state(CustomStates.CUSTOM_START_DATE)
        return

    rows = await get_work_time(callback_query.from_user.id, start_date, end_date)
    unfilled = await get_unfilled(callback_query.from_user.id, start_date, end_date)
    await callback_query.message.answer("Найденные рабочие смены:")
    total_minutes = 0
    for row in rows:
        date = row[0]
        start_time = row[1]
        end_time = row[2]
        hours = row[3]
        minutes = calculate_total(hours)
        total_minutes += minutes
        await callback_query.message.answer(f"Дата: {date}, Начало: {start_time}, Конец: {end_time}, Часов: {hours}\n")
    await callback_query.message.answer(f"Общее количество часов: {total_minutes // 60}:{total_minutes % 60}\n")
    if unfilled:
        await callback_query.message.answer("Имеются незакрытые смены!\n"
                                            "Ты можешь их закрыть, нажав на кнопку и введя время окончания работы.", reply_markup=get_keyboard(unfilled))
    else:
        await callback_query.message.answer("Все смены за выбранные период закрыты")

    await state.clear()


# Обработчик кастомного периода
@get_work_router.callback_query(SimpleCalCallback.filter(), CustomStates.CUSTOM_START_DATE)
async def set_custom_start_date(callback_query: types.CallbackQuery, callback_data: SimpleCalCallback,
                                state: FSMContext):
    start_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if start_date:
        await callback_query.message.answer(start_date.strftime('%Y-%m-%d'))
    await state.update_data(start_date=start_date.strftime('%Y-%m-%d'))
    await callback_query.message.answer("Выбери конец периода: ", reply_markup=SimpleCalendar().start_calendar())
    await state.set_state(CustomStates.CUSTOM_END_DATE)


# Обработчик кастомного периода
@get_work_router.callback_query(SimpleCalCallback.filter(), CustomStates.CUSTOM_END_DATE)
async def set_custom_end_date(callback_query: types.CallbackQuery, callback_data: SimpleCalCallback, state: FSMContext):
    end_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if end_date:
        await callback_query.message.answer(end_date.strftime('%Y-%m-%d'))
    await state.update_data(end_date=end_date.strftime('%Y-%m-%d'))
    data = await state.get_data()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    rows = await get_work_time(callback_query.from_user.id, start_date, end_date)
    unfilled = await get_unfilled(callback_query.from_user.id, start_date, end_date)
    await callback_query.message.answer("Найденные рабочие смены за выбранный период времени:")

    total_minutes = 0
    for row in rows:
        date = row[0]
        start_time = row[1]
        end_time = row[2]
        hours = row[3]
        minutes = calculate_total(hours)
        total_minutes += minutes
        await callback_query.message.answer(
            f"Дата: {date}, Начало: {start_time}, Конец: {end_time}, Часов: {hours}\n")
    await callback_query.message.answer(f"Общее рабочее время: {total_minutes // 60}:{total_minutes % 60}\n")
    if unfilled:
        await callback_query.message.answer("Имеются незакрытые смены!\n"
                                            "Ты можешь их закрыть, нажав на кнопку и введя время окончания работы.",
                                            reply_markup=get_keyboard(unfilled))
    else:
        await callback_query.message.answer("Все смены за выбранные период закрыты")
    await state.clear()
