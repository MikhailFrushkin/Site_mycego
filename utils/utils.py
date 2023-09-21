from loguru import logger
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def df_in_xlsx(df, filename, max_width=50):
    # Создание нового рабочего книги Excel
    workbook = Workbook()
    # Создание нового листа в рабочей книге
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
        else:
            week = today.isocalendar()[1] + 1
        logger.error('ошибка', ex)
    return year, week


def get_dates(year, week_number):
    import datetime
    # Создаем объект даты для первого дня года
    first_day_of_year = datetime.date(year, 1, 1)
    # Вычисляем дату понедельника первой недели года
    days_to_add = 0 - first_day_of_year.weekday()
    monday_of_week_1 = first_day_of_year + datetime.timedelta(days=days_to_add)
    # Вычисляем дату понедельника заданной недели
    days_to_add = (week_number) * 7
    monday_of_given_week = monday_of_week_1 + datetime.timedelta(days=days_to_add)

    # Вычисляем дату воскресенья заданной недели
    sunday_of_given_week = monday_of_given_week + datetime.timedelta(days=6)

    return monday_of_given_week, sunday_of_given_week
