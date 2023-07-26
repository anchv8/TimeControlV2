from typing import Optional

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.api.end_work import set_end_work
from src.states import EditKeyboardStates

kb_router = Router()


class EditWorkCallback(CallbackData, prefix='getw_'):
    action: str
    value: Optional[str]


def get_keyboard(rows) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardBuilder()

    for i in rows:
        date = i[0]
        start_time = i[1]
        inline_kb.row(InlineKeyboardButton(
            text=f"Дата: {date},\n "
                 f"Время начала: {start_time}",
            callback_data=EditWorkCallback(action='edit',
                                           value=date.strftime("%Y-%m-%d")).pack()))

    inline_kb.adjust(1)
    return inline_kb.as_markup()


@kb_router.callback_query(EditWorkCallback.filter(F.action == 'edit'))
async def process_edit_work(callback: CallbackQuery, callback_data: EditWorkCallback, state: FSMContext):
    edit_date = callback_data.value
    await state.update_data(edit_date=edit_date)
    if callback_data.action == 'edit':
        await callback.message.answer('Введи время окончания работы в формате ЧЧ:ММ')
        await state.set_state(EditKeyboardStates.EDIT_END_TIME)


@kb_router.message(EditKeyboardStates.EDIT_END_TIME)
async def set_edit_work(message: Message, state: FSMContext):
    edit_end_time = message.text.strip()
    await state.update_data(edit_end_time=edit_end_time)
    data = await state.get_data()
    user_id = message.from_user.id
    edit_date = data.get('edit_date')
    edit_end_time = data.get('edit_end_time')
    await set_end_work(edit_end_time, user_id, edit_date)
    await message.answer("Дата успешно отредактирована!")
    await state.clear()
