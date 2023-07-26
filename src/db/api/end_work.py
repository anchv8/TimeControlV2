# Запись времени окончания работы в таблицу work_time
from datetime import datetime, time


from src.db.engine import get_pool
from src.utils.utils import calculate_duration


async def get_start_time(tg_id, work_date):
    pool = await get_pool()
    async with pool.acquire() as conn:
        start_time = await conn.fetchval("SELECT start_time FROM work_time WHERE user_id = $1 AND date = $2",
                                         tg_id, work_date)
        start_time_str = time.strftime(start_time, '%H:%M')
        return start_time_str


async def set_end_work(end_time, user_id, date):
    pool = await get_pool()
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    end_time_obj = datetime.strptime(end_time, "%H:%M")
    duration = await calculate_duration(await get_start_time(user_id, date_obj), end_time)
    # Обновление значения end_work и записывает total_time
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE work_time SET end_time = $1, total_time = $2 WHERE user_id = $3 AND date = $4",
            end_time_obj, duration, user_id, date_obj)
        return result
