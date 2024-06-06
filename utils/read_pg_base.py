from datetime import datetime, timedelta
from pprint import pprint
import pytz
import psycopg2
from environs import Env
from loguru import logger

env = Env()
env.read_env()
env_dict = env.dump()
print(env_dict)

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
        "password": password,
    }
    db_params2 = {
        "host": host,
        "database": dbname2,
        "user": user,
        "password": password,
    }
    data = {}
    date_pre = datetime.now().date() - timedelta(days=5)

    utc_timezone = pytz.UTC
    for index, i in enumerate([db_params, db_params2]):
        try:
            with psycopg2.connect(**i) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT name_file, 
                                   COUNT(*) AS record_count, 
                                   MIN(update_timestamp) AS first_update_timestamp,
                                   JSONB_OBJECT_AGG(num_on_list, 
                                                    JSONB_BUILD_OBJECT('quantity', num, 'art', art, 'comp', machin)) 
                                                    AS art_dict, 
                                   MIN(lists)
                           FROM orders
                           WHERE update_timestamp > %s 
                             AND name_file IS NOT NULL
                             AND (update_timestamp, num_on_list, num, art) IS NOT NULL
                           GROUP BY name_file
                        """, (date_pre,)
                    )

                    rows = cursor.fetchall()
                    for row in rows:
                        name_file, record_count, first_update_timestamp, art_dict, lists = row

                        created_at_utc = utc_timezone.localize(first_update_timestamp) - timedelta(hours=4)

                        data[name_file] = {
                            'createdAt': created_at_utc,
                            'products_count': record_count,
                            'products': [],
                            'products_nums_on_list': art_dict if '0' not in art_dict else {},
                            'lists': lists,
                            'type': 'Программа',
                            "type_d": 'badges' if index == 0 else 'posters'
                        }

        except Exception as ex:
            logger.error(ex)
    # pprint(data)
    logger.success(len(data))
    return data


if __name__ == '__main__':
    update_base_postgresql()
