from aiogram import types, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from src.db.api.end_work import set_end_work
from src.db.api.utils import is_end_time_set
from src.middlewares.is_register import IsRegister
from src.states import DateTimeStates

end_work_router = Router()
end_work_router.message.middleware(IsRegister())


# Команда записи времени окончания работы
@end_work_router.message(Command('endwork'))
@end_work_router.message(Text('⌛ Конец работы'))
async def end_work(message: types.Message, state: FSMContext):
    await state.clear()
    check = await is_end_time_set(message.from_user.id, message.date.strftime("%Y-%m-%d"))
    if check == "ok":
        await message.answer("Введи время окончания работы в формате ЧЧ:ММ")
        await state.set_state(DateTimeStates.END_TIME)
    elif check == "no result":
        await message.answer(
            "Отметка о начале работы за сегодня не найдена! Если нужно закрыть вчерашнюю смену, воспользуйся командой /edit_work")
    elif check == "err":
        await message.answer("Время окончания работы за сегодня уже записано!")
    else:
        await message.answer("Непредвиденная ошибка")


# Обработка сообщения об окончании работы
@end_work_router.message(DateTimeStates.END_TIME)
async def process_end_work(message: types.Message, state: FSMContext):
    try:
        hours, minutes = map(int, message.text.split(":"))
        if (0 <= hours <= 24) and (0 <= minutes <= 60):
            await state.update_data(end_time=message.text)
            data = await state.get_data()
            await state.set_data(data)
            end_time = data.get('end_time')
            await set_end_work(end_time, message.from_user.id, message.date.strftime("%Y-%m-%d"))
            await message.answer("Работа окончена! Время записано")
            await state.clear()
        else:
            await message.answer("Некорректно введено время! Попробуй снова")
    except ConnectionError:
        await message.answer("Непредвиденная ошибка")
