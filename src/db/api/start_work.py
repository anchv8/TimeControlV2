# Запись времени начала работы в таблицу work_time
from datetime import datetime

from src.db.engine import get_pool


async def set_start_work(user_id, date, start_time):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    time_obj = datetime.strptime(start_time, "%H:%M")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO work_time (user_id, date, start_time) VALUES ($1, $2, $3)",
                           user_id, date_obj, time_obj)
