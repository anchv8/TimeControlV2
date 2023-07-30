# Добавление сотрудника в таблицу employee
from src.db.engine import get_pool


async def register(user_tg_id, full_name, mobile_number, department):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO employees (user_tg_id, full_name, mobile_number, department) VALUES ($1, $2, $3, $4)",
            user_tg_id, full_name, mobile_number, department)
