import os
from datetime import datetime

import pandas as pd
from aiogram import types, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram3b8_calendar import SimpleCalCallback, SimpleCalendar
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from src.db.api.get_xlsx import xlsx_query_all, xlsx_query_dep
from src.db.api.utils import check_access, get_dep
from src.middlewares.is_register import IsRegister
from src.states import XlsxState

get_xlsx_router = Router()
get_xlsx_router.message.middleware(IsRegister())


def calculate_total_hours(df):
    df['total_time'] = pd.to_timedelta(df['total_time'].astype(str))
    grouped_df = df.groupby(['full_name'])['total_time'].sum().reset_index()
    return grouped_df


async def access(user_id):
    return await check_access(user_id)


@get_xlsx_router.message(Command('xlsx'))
@get_xlsx_router.message(Text('🗄️ Табель (для руководителей отделов)'))
async def excel(message: types.Message, state: FSMContext):
    if await access(message.from_user.id) != 0:
        await message.answer("Выбери начало периода: ",
                             reply_markup=SimpleCalendar().start_calendar())
        await state.set_state(XlsxState.START_PERIOD)
    else:
        await message.answer("Недостаточно прав для выплнения команды")


@get_xlsx_router.callback_query(SimpleCalCallback.filter(), XlsxState.START_PERIOD)
async def process_excel(callback_query: types.CallbackQuery, callback_data: SimpleCalCallback, state: FSMContext):
    xlsx_start = await SimpleCalendar().process_selection(callback_query, callback_data)
    if xlsx_start:
        await callback_query.message.answer(xlsx_start.strftime('%Y-%m-%d'))
    await state.update_data(xlsx_start=xlsx_start.strftime('%Y-%m-%d'))
    await callback_query.message.answer("Выбери конец периода: ",
                                        reply_markup=SimpleCalendar().start_calendar())
    await state.set_state(XlsxState.END_PERIOD)


@get_xlsx_router.callback_query(SimpleCalCallback.filter(), XlsxState.END_PERIOD)
async def process_excel_end(callback_query: types.CallbackQuery, callback_data: SimpleCalCallback, state: FSMContext):
    xlsx_end = await SimpleCalendar().process_selection(callback_query, callback_data)
    if xlsx_end:
        await callback_query.message.answer(xlsx_end.strftime('%Y-%m-%d'))
    await state.update_data(xlsx_end=xlsx_end.strftime('%Y-%m-%d'))
    data = await state.get_data()
    start_date = data.get('xlsx_start')
    end_date = data.get('xlsx_end')

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    check = await get_dep(callback_query.from_user.id)
    dep_str = " ".join(check)

    if dep_str == 'Бухгалтерия' or await access(callback_query.from_user.id) == 3:
        df = pd.DataFrame.from_records(await xlsx_query_all(start_date, end_date),
                                       columns=['full_name', 'department', 'date', 'total_time'])
    else:
        df = pd.DataFrame.from_records(await xlsx_query_dep(dep_str, start_date, end_date),
                                       columns=['full_name', 'department', 'date', 'total_time'])

    grouped_df = calculate_total_hours(df)  # Вычисление суммы часов для каждого сотрудника

    # Создание пустого списка строк
    rows = []
    # Группировка данных по отделам и заполнение списка строк
    for group_key, group_data in df.groupby(['department', 'full_name']):
        department, full_name = group_key
        row = [department, full_name] + [''] * len(date_range)

        for _, data_row in group_data.iterrows():
            date = datetime.strftime(data_row['date'], "%Y-%m-%d")
            total_time = data_row['total_time']
            index = date_range.get_loc(date)
            row[index + 3] = total_time

            # Добавление суммы часов для текущего сотрудника в конец строки
        total_hours_sum = \
            grouped_df[(grouped_df['full_name'] == full_name)]['total_time'].iloc[0]
        row.append(total_hours_sum)

        rows.append(row)

    # Создание DataFrame из списка строк
    columns = ['Отдел', 'ФИО'] + date_range.strftime('%Y-%m-%d').tolist() + ['Всего часов']
    grouped_df = pd.DataFrame(rows, columns=columns)

    # Создание объекта Workbook
    workbook = Workbook()

    # Получение листа по умолчанию и его название
    worksheet = workbook.active
    worksheet.title = 'Data'

    # Запись заголовков столбцов
    headers = columns
    worksheet.append(headers)

    # Запись данных в лист
    for _, row in grouped_df.iterrows():
        worksheet.append(row.tolist())

    # Автоподбор ширины столбцов
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
        worksheet.column_dimensions[column_cells[0].column_letter].alignment = Alignment(horizontal='center')

    # Применение форматирования к столбцу с суммарными рабочими часами
    total_hours_column_letter = worksheet.cell(row=1, column=len(columns)).column_letter
    total_hours_cells = worksheet[total_hours_column_letter][1:]
    for cell in total_hours_cells:
        cell.font = Font(bold=True)

    # Сохранение файла
    excel_file = f'Табель {start_date}-{end_date}.xlsx'
    workbook.save(excel_file)

    # Отправка Excel-файла пользователю
    with open(excel_file, 'rb') as file:
        await callback_query.message.answer_document(BufferedInputFile(file.read(), filename=excel_file))

    # Удаление временного Excel-файла
    os.remove(excel_file)

    await callback_query.message.answer(f'Табель за период с {start_date} по {end_date}')
