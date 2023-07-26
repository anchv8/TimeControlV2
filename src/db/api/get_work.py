# Получение данных о рабочем времени из таблицы work_time
from datetime import datetime

from src.db.engine import get_pool


async def get_work_time(user_id, start_date, end_date):
    pool = await get_pool()
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    async with pool.acquire() as conn:
        result = await conn.fetch(
            """SELECT date, start_time, end_time, total_time FROM work_time
            WHERE end_time IS NOT NULL 
            AND user_id = $1
            AND date BETWEEN $2 AND $3 ORDER BY date""",
            user_id, start_date_obj, end_date_obj
        )
        return result

