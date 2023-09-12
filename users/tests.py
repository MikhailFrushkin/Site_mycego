import random
import string

import pandas as pd

from utils.utils import df_in_xlsx


def process_text(text):
    if isinstance(text, str):
        text = text.lower().strip().capitalize()
    return text


def generate_password():
    # Генерация случайного пароля с минимум 8 символами и минимум 4 буквами (английскими) и цифрами
    password_length = random.randint(8, 12)  # Выбираем случайную длину пароля от 8 до 12 символов
    letters = string.ascii_letters  # Получаем все буквы английского алфавита (верхний и нижний регистры)
    digits = string.digits  # Получаем все цифры
    password = ''.join(random.choice(letters + digits) for _ in range(password_length))  # Генерируем пароль
    return password


def create_nickname(row):
    last_name = row['Фамилия']
    first_name = row['Имя']
    if isinstance(last_name, str) and isinstance(first_name, str) and len(first_name) > 0:
        return f"{last_name}_{first_name}"
    else:
        return ''


def main():
    df = pd.read_excel('Пользователи для импорта.xlsx')
    for column in df.columns:
        df[column] = df[column].apply(process_text)

    # Создание столбца "Ник"
    df['Ник'] = df.apply(create_nickname, axis=1)
    df['Пароль'] = [generate_password() for _ in range(len(df))]
    # Вывод обновленного DataFrame
    print(df)

    df_in_xlsx(df, 'Пользователи для импорта(ред)')


if __name__ == '__main__':
    main()
