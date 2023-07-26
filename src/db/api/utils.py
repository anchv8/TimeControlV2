# Проверка наличия пользователя в таблице employee
from datetime import datetime

from src.db.engine import get_pool


async def is_exist(user_tg_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("SELECT * FROM employees WHERE user_tg_id = $1", user_tg_id)
        return bool(result)


# Проверка наличия "не закрытой" записи с началом работы
async def is_start_time_set(user_tg_id: int, date: datetime.date) -> bool:
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """SELECT 1 FROM work_time
          WHERE user_id = $1 AND date = $2  
          """,
            user_tg_id, date_obj)
        return bool(result)


async def is_end_time_set(user_id, date):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
        SELECT * FROM work_time WHERE user_id = $1 AND date = $2 AND start_time IS NOT NULL""",
                                     user_id, date_obj)
        if result is None:
            return "no result"
        elif result[3]:
            return "err"
        else:
            return "ok"


async def check_access(user_tg_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT access_level FROM employees WHERE user_tg_id = $1", user_tg_id)
        return result


async def get_unfilled(user_id, start_date, end_date):
    pool = await get_pool()
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    async with pool.acquire() as conn:
        result = await conn.fetch(
            """
            SELECT date, start_time FROM work_time
            WHERE user_id = $1
            AND end_time IS NULL
            AND date BETWEEN $2 AND $3
            ORDER BY date                
            """, user_id, start_date_obj, end_date_obj
        )
    return result


async def auto_get_unfilled(start_date, end_date):
    pool = await get_pool()
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    print(start_date_obj)
    print(type(start_date_obj))
    print(end_date_obj)
    print(type(end_date_obj))
    async with pool.acquire() as conn:
        result = await conn.fetch(
            """
            SELECT user_id, date, start_time FROM work_time
            WHERE end_time IS NULL
            AND date BETWEEN $1 AND $2
            ORDER BY date                
            """, start_date_obj, end_date_obj
        )
    return result


async def get_user_tg_id():
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch("""SELECT user_tg_id FROM employees""")
        return result


async def get_dep(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT department FROM employees WHERE user_tg_id = $1",
            user_id)
        return result
