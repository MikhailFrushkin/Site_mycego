import calendar
from datetime import date, timedelta

from loguru import logger
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def df_in_xlsx(df, filename, max_width=50):
    workbook = Workbook()
    sheet = workbook.active
    # Конвертация DataFrame в строки данных
    for row in dataframe_to_rows(df, index=False, header=True):
        sheet.append(row)
    for column in sheet.columns:
        column_letter = column[0].column_letter
        max_length = max(len(str(cell.value)) for cell in column)
        adjusted_width = min(max_length + 2, max_width)
        sheet.column_dimensions[column_letter].width = adjusted_width
    # Сохранение рабочей книги в файл
    workbook.save(f"{filename}.xlsx")


def get_year_week(data, type=None):
    import datetime
    try:
        year = data['year']
        week = data['week']
    except Exception as ex:
        today = datetime.date.today()
        year = today.year
        if type == 'list_work' or type == 'salary':
            week = today.isocalendar()[1]
        elif type == 'finger':
            week = today.isocalendar()[1] - 1
        else:
            week = today.isocalendar()[1] + 1
    return year, week


def get_dates(year, week_number):
    from datetime import datetime, timedelta
    # Находим первый день года
    jan_first = datetime(year, 1, 1)
    # Определяем день недели для 1 января
    day_of_week = jan_first.isoweekday()

    # Если 1 января - понедельник, вторник, среда или четверг, то это первая неделя
    if day_of_week < 5:
        start_delta = -day_of_week + 1
    else:
        # Иначе первая неделя начнется в следующем году
        start_delta = 8 - day_of_week

    # Находим начало и конец нужной недели
    start_date = jan_first + timedelta(days=start_delta) + timedelta(weeks=week_number - 1)
    end_date = start_date + timedelta(days=6)

    return start_date, end_date


def get_days_for_current_and_next_month(year, month):
    # Получаем первый день текущего месяца
    first_day_of_current_month = date(year, month, 1)

    # Получаем первый день следующего месяца
    if month == 12:
        first_day_of_next_month = date(year + 1, 1, 1)
    else:
        first_day_of_next_month = date(year, month + 1, 1)

    # Получаем последний день текущего месяца
    last_day_of_current_month = date(year, month, calendar.monthrange(year, month)[1])

    # Создаем список дней для текущего месяца
    days_for_current_and_next_month = []
    current_day = first_day_of_current_month
    while current_day <= last_day_of_current_month:
        days_for_current_and_next_month.append(current_day)
        current_day += timedelta(days=1)

    return first_day_of_current_month, last_day_of_current_month, days_for_current_and_next_month