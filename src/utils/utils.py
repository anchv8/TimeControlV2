from datetime import datetime, time, timedelta
import datetime as dt


# Функция для подсчета отработанного времени. Используется в set_end_work и set_edit_datetime
async def calculate_duration(start_time, end_time):
    if isinstance(start_time, (datetime, timedelta, time)) or isinstance(end_time, (datetime, timedelta, time)):
        start_time_str = start_time.strftime('%H:%M')
        end_time_str = end_time.strftime('%H:%M')
    elif isinstance(start_time, str) and isinstance(end_time, str):
        start_time_str = start_time
        end_time_str = end_time
    # Разбиваем время из сообщения для перевода в минуты
    start_hours, start_minutes = map(int, start_time_str.split(":"))
    end_hours, end_minutes = map(int, end_time_str.split(":"))

    # Считаем минуты
    duration_minutes = (end_hours * 60 + end_minutes) - (start_hours * 60 + start_minutes)

    # Делаем timedelta объект
    duration = (timedelta(minutes=duration_minutes) + dt.datetime.min).time()

    return duration


# Перевод часы в минуты
def calculate_total(time_obj):

    time_str = time_obj.strftime('%H:%M:%S')
    hours, minutes, seconds = map(int, time_str.split(":"))
    total_minutes = (hours * 60 + minutes)
    return total_minutes


# получаем даты месяца
async def get_month_dates():
    today = dt.date.today()
    start_date = today.replace(day=1)
    next_month = start_date.replace(day=28) + dt.timedelta(days=4)
    end_date = next_month - dt.timedelta(days=next_month.day)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


# Получаем даты недели
async def get_week_dates():
    today = dt.date.today()
    start_date = today - dt.timedelta(days=today.weekday())
    end_date = start_date + dt.timedelta(days=6)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
