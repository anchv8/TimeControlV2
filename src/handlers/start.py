from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.api.start import register
from src.db.api.utils import is_exist
from src.states import RegStates

start_router = Router(name='start')


# Обработчики сообщений с регистрацией
@start_router.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    if not await is_exist(message.from_user.id):
        await message.answer("Привет! Нужно тебя зарегистрировать в системе, для этого следуй шагам ниже\n\n"
                             "Введи ФИО:")
        await state.set_state(RegStates.FULL_NAME)
    else:
        await message.answer("Ты уже зарегистрирован(-а)! Для отметки о начале работы...")


@start_router.message(RegStates.FULL_NAME)
async def process_last_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    if not full_name:
        await message.answer("Invalid input. Попробуй снова.")
        return

    await state.update_data(full_name=full_name)
    await message.answer("Теперь нужен твой номер телефона.")
    await state.set_state(RegStates.MOBILE_NUMBER)


# Обрабатываем запрос с номером телефона
@start_router.message(RegStates.MOBILE_NUMBER)
async def process_mobile_number(message: types.Message, state: FSMContext):
    mobile_number = message.text.strip()
    if not mobile_number.isdigit():
        await message.answer("Invalid input. Попробуй снова.")
        return

    await state.update_data(mobile_number=mobile_number)
    await message.answer("И последнее. В каком отделе ты работаешь?")

    # Клавиатура для выбора отдела
    departments = ["IT", "Бухгалтерия", "Маркетплейсы и ОПТ", "Склад", "Администрация", "Розница", "Маркетинг",
                   "Интернет магазин"]
    keyboard = InlineKeyboardBuilder()

    for department in departments:
        keyboard.add(types.InlineKeyboardButton(text=department, callback_data=department))
    keyboard.adjust(3, 2)
    await message.answer("Выбери свой отдел:", reply_markup=keyboard.as_markup())
    await state.set_state(RegStates.DEPARTMENT)


# Обработчик коллбэка от клавиатуры
@start_router.callback_query(RegStates.DEPARTMENT)
async def process_department(callback_query: types.CallbackQuery, state: FSMContext):
    department = callback_query.data

    data = await state.get_data()
    data['department'] = department
    await state.set_data(data)

    # Разгружаем данные из FSM
    user_tg_id = callback_query.from_user.id
    full_name = data.get('full_name')
    mobile_number = int(data.get('mobile_number'))

    # Кладем данные в базу
    await register(user_tg_id, full_name, mobile_number, department)

    await callback_query.message.answer(
        "Регистрация окончена! Теперь с помощью команды /startwork делай отметку о начале работы, а с помощью "
        "/endwork об окончании.")

    # Закрываем FSM
    await state.clear()
