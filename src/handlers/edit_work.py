from aiogram import types, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram3b8_calendar import SimpleCalCallback, SimpleCalendar

from src.db.api.edit_work import set_edit_datetime
from src.middlewares.is_register import IsRegister
from src.states import EditStates

edit_work_router = Router()
edit_work_router.message.middleware(IsRegister())


# Команда редактирования даты и времени
@edit_work_router.message(Command('editwork'))
@edit_work_router.message(Text('✏️ Изменить время'))
async def edit_work_day(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Выбери день для редактирования: ",
                         reply_markup=SimpleCalendar().start_calendar())
    await state.set_state(EditStates.DATE)


@edit_work_router.callback_query(SimpleCalCallback.filter(), EditStates.DATE)
async def edit_start_work(callback_query: types.CallbackQuery, callback_data: SimpleCalCallback, state: FSMContext):
    edit_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if edit_date:
        await callback_query.message.answer(edit_date.strftime('%Y-%m-%d'))
        await state.update_data(edit_date=edit_date.strftime('%Y-%m-%d'))
        await callback_query.message.answer("Введи время начала работы в формате ЧЧ:ММ.")
        await state.set_state(EditStates.EDIT_START_TIME)


@edit_work_router.message(EditStates.EDIT_START_TIME)
async def edit_end_work(message: types.Message, state: FSMContext):
    edit_start_time = message.text.strip()
    await state.update_data(edit_start_time=edit_start_time)
    await message.answer("Введи время окончания работы в формате ЧЧ:ММ.")
    await state.set_state(EditStates.EDIT_END_TIME)


@edit_work_router.message(EditStates.EDIT_END_TIME)
async def set_edit(message: types.Message, state: FSMContext):
    edit_end_time = message.text.strip()
    await state.update_data(edit_end_time=edit_end_time)
    data = await state.get_data()
    await state.set_data(data)
    user_id = message.from_user.id
    edit_date = data.get('edit_date')
    edit_start_time = data.get('edit_start_time')
    edit_end_time = data.get('edit_end_time')
    await set_edit_datetime(user_id, edit_date, edit_start_time, edit_end_time)
    await message.answer("Дата успешно отредактирована!")
    await state.clear()
