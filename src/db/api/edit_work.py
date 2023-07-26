# Редактирование времени работы
from datetime import datetime

from src.db.engine import get_pool
from src.utils.utils import calculate_duration


async def set_edit_datetime(user_id, date, start_time, end_time):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing_record = await conn.fetch("SELECT * FROM work_time WHERE user_id = $1 AND date = $2", user_id, date_obj)
        duration = await calculate_duration(start_time_obj, end_time_obj)
        if existing_record:
            # Если запись была, то обновляем
            await conn.execute(
                "UPDATE work_time SET start_time = $1, end_time = $2, total_time = $3 WHERE user_id = $4 AND date = $5",
                start_time_obj, end_time_obj, duration, user_id, date_obj)
        else:
            # Делаем новую, если записи не было
            await conn.execute(
                "INSERT INTO work_time (user_id, date, start_time, end_time, total_time) VALUES ($1, $2, $3, $4, $5)",
                user_id, date_obj, start_time_obj, end_time_obj, duration)

