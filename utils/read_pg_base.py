from datetime import datetime, timedelta
from pprint import pprint
import pytz
import psycopg2
from environs import Env
from loguru import logger

env = Env()
env.read_env()
machine_name = env.str('machine_name')
dbname = env.str('dbname')
dbname2 = env.str('dbname2')
user = env.str('user')
password = env.str('password')
host = env.str('host')


def update_base_postgresql():
    db_params = {
        "host": host,
        "database": dbname,
        "user": user,
        "password": password
    }
    db_params2 = {
        "host": host,
        "database": dbname2,
        "user": user,
        "password": password
    }
    data = {}
    date_pre = datetime.now().date() - timedelta(days=5)

    utc_timezone = pytz.UTC  # Часовой пояс UTC
    possible_entries = ['zon', 'зон']
    try:
        with psycopg2.connect(**db_params) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM files ")
                rows = cursor.fetchall()

                for row in rows:
                    if (row[1].date() > date_pre) and any(entry in row[2].lower() for entry in possible_entries):
                        created_at_utc = utc_timezone.localize(row[1])

                        data[row[2]] = {
                            'createdAt': created_at_utc,
                            'products_count': row[3],
                            'type': 'Программа'
                        }
        print(len(data))
    except Exception as ex:
        logger.error(ex)

    try:
        with psycopg2.connect(**db_params2) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT name_file, COUNT(*) AS record_count, MIN(update_timestamp)
                    AS first_update_timestamp FROM orders GROUP BY name_file""")
                rows = cursor.fetchall()
                for row in rows:
                    name_file, record_count, first_update_timestamp = row
                    if (first_update_timestamp.date() > date_pre) and any(entry in name_file.lower() for entry in possible_entries):
                        created_at_utc = utc_timezone.localize(first_update_timestamp)

                        data[name_file] = {
                            'createdAt': created_at_utc,
                            'products_count': record_count,
                            'type': 'Программа'
                        }
        print(len(data))
    except Exception as ex:
        logger.error(ex)
    return data


if __name__ == '__main__':
    print(update_base_postgresql())