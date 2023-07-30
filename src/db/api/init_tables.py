
from src.db.engine import get_pool


async def create_table_employees():
    pool = await get_pool()
    async with pool.acquire() as connection:
        data = await connection.execute(
            """ 
            CREATE TABLE IF NOT EXISTS employees (
            user_tg_id BIGINT NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            mobile_number BIGINT NOT NULL,
            department VARCHAR(255),
            access_level INT DEFAULT 0,
            PRIMARY KEY (user_tg_id))
            """)
        return data


async def create_table_worktime():
    pool = await get_pool()
    async with pool.acquire() as connection:
        data = await connection.execute("""
            CREATE TABLE IF NOT EXISTS work_time (
            user_id BIGINT NOT NULL REFERENCES employees(user_tg_id),
            date DATE,
            start_time TIME,
            end_time TIME,
            total_time TIME)
            """)
    return data


async def run_tables():
    await create_table_employees()
    await create_table_worktime()
