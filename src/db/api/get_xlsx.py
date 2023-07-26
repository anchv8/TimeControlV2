from datetime import datetime

from src.db.engine import get_pool

# Выполнение запроса для получения данных одного отдела из базы данных

query_dep = """
        SELECT employees.full_name, employees.department, work_time.date, work_time.total_time
        FROM work_time
        JOIN employees ON employees.user_tg_id = work_time.user_id
        WHERE department = $1 AND work_time.date BETWEEN $2 AND $3 AND work_time.total_time IS NOT NULL
    """

# Выполнение запроса для получения данных всех отделов из базы данных
query_all = """
        SELECT employees.full_name, employees.department, work_time.date, work_time.total_time
        FROM work_time
        JOIN employees ON employees.user_tg_id = work_time.user_id
        WHERE work_time.date BETWEEN $1 AND $2 AND work_time.total_time IS NOT NULL
    """


async def xlsx_query_all(start_date, end_date):
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch(query_all, start_date_obj, end_date_obj)
        print(result)
        print(type(result))
        return result


async def xlsx_query_dep(dep_str, start_date, end_date):
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch(query_dep, dep_str, start_date_obj, end_date_obj)
        return result
