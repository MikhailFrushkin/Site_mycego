import json
import os
import re
import time
from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.db import transaction
from loguru import logger

from completed_works.models import Delivery, DeliveryState
from utils.read_pg_base import update_base_postgresql

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycego.settings')
from mycego.settings import api_key1, api_key2


def parser_wb_cards(api_key: str, seller: str = None) -> list[dict]:
    """Получение карточек товаров"""
    api_url = "https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    limit = 1000  # Максимальное количество запрашиваемых КТ
    result = []  # Здесь будем хранить все полученные данные
    data = {
        "sort": {
            "cursor": {
                "limit": limit,
            },
            "filter": {
                "withPhoto": -1,
            },
            "sort": {
                "sortColumn": "updateAt",
                "ascending": False
            }
        }
    }

    while True:
        time.sleep(3)
        data_json = json.dumps(data)

        # Выполняем POST-запрос с данными в формате JSON
        response = requests.post(api_url, headers=headers, data=data_json)

        if response.status_code == 200:
            response_data = response.json()
            result.extend(response_data.get("data", []).get("cards", []))
            total = response_data['data']['cursor']['total']
            nmID = response_data['data']['cursor']['nmID']
            updatedAt = response_data['data']['cursor']['updatedAt']
            current_count = len(result)
            print(f"Получено {current_count}")

            if total < limit:
                break
            # Обновляем курсор для следующего запроса
            data["sort"]["cursor"]["updatedAt"] = updatedAt
            data["sort"]["cursor"]["nmID"] = nmID
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            break

    with open(f'files/wildberries_data_cards{seller}.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Все данные сохранены в файл 'wildberries_data_cards{seller}.json'")
    return result


def parser_wb_delivery(api_key: str, seller: str = None) -> tuple[list[dict], str]:
    """Получение поставок"""
    api_url = "https://suppliers-api.wildberries.ru/api/v3/supplies"
    headers = {
        "Authorization": api_key
    }
    limit = 1000
    result = []
    data = {
        "next": 0,
        "limit": limit
    }
    current_time = datetime.now(pytz.utc)
    # Определяем временной интервал в неделю (7 дней)
    week_interval = timedelta(days=5)

    while True:
        response = requests.get(api_url, headers=headers, params=data)

        if response.status_code == 200:
            response_data = response.json()

            count = len(response_data['supplies'])
            for delivery in response_data.get("supplies", []):
                created_at = datetime.fromisoformat(delivery["createdAt"].replace('Z', '+00:00')).replace().replace(
                    tzinfo=pytz.utc)
                time_difference = current_time - created_at

                if time_difference < week_interval:
                    result.append(delivery)

            data['next'] = response_data['next']
            print(f'Отсканировано {len(result)}')

            if count < limit:
                break
        else:
            print(f"Ошибка {response.status_code}: {response.text}")

    with open(f'files/wildberries_data_delivery{seller}.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Все данные сохранены в файл 'wildberries_data_delivery_{seller}.json'")
    return result, seller


def parser_wb_get_details(api_key, supplyId):
    """Получение деталей поставки"""
    api_url = f"https://suppliers-api.wildberries.ru/api/v3/supplies/{supplyId}/orders"
    headers = {
        "Authorization": api_key
    }
    result = {}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if response_data:
            result['arts'] = []
            result['sum_price'] = 0
            for item in response_data.get("orders", []):
                try:
                    result['arts'].append(item['article'])
                    result['sum_price'] += item['price']
                except Exception as ex:
                    logger.error(ex)
                    logger.error(item)
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
    # with open(f'files/wildberries_data_delivery_{supplyId}.json', 'w', encoding='utf-8') as file:
    #     json.dump(result, file, indent=4, ensure_ascii=False)
    #
    # print(f"Все данные сохранены в файл 'wildberries_data_delivery_{supplyId}.json'")
    return result


def result_list_data(delivery_list, api_key, data_list=None, seller=None):
    if not data_list:
        data_list = []
    for index, item in enumerate(delivery_list):
        try:
            info = parser_wb_get_details(api_key=api_key, supplyId=item['id'])
            item['products_count'] = len(info['arts'])
            item['products'] = info['arts']
            item['price'] = info['sum_price']
            item['type'] = seller
            for i in item['products']:
                if 'POSTER-' in i:
                    item['type_d'] = 'posters'
                    break
            else:
                item['type_d'] = 'badges'
            data_list.append(item)
        except Exception as ex:
            logger.error(ex)
    return data_list


@transaction.atomic
def create_rows_delivery(data_list=None):
    data_pg = update_base_postgresql()
    logger.success(len(data_pg))

    try:
        state_badge = DeliveryState.objects.get(name='Печать', type='Значки')
        state_poster = DeliveryState.objects.get(name='Печать', type='Постеры')
    except Exception as ex:
        logger.error(ex)
        return

    if data_list:
        for data in data_list:
            pattern = r'[\\/:"*?<>|]'
            name = re.sub(pattern, '', data['name'])
            delivery_instance = Delivery.objects.filter(name=name, createdAt=data['createdAt']).order_by(
                'createdAt').first()

            if delivery_instance:
                delivery_instance.closedAt = data['closedAt']
                delivery_instance.scanDt = data['scanDt']
                delivery_instance.done = data['done']
                delivery_instance.save()
            else:
                try:
                    created_ins = Delivery(
                        id_wb=data['id'],
                        name=name,
                        createdAt=data['createdAt'],
                        closedAt=data['closedAt'],
                        scanDt=data['scanDt'],
                        done=data['done'],
                        products_count=data['products_count'],
                        products=data['products'],
                        price=data['price'],
                        type=data['type'],
                        type_d=data['type_d'],
                        state=state_poster if data['type_d'] == 'posters' else state_badge,

                    )
                    created_ins.save()
                except Exception as ex:
                    logger.error(ex)
    if data_pg:
        for key, value in data_pg.items():
            pattern = r'[\\/:"*?<>|]'
            name = re.sub(pattern, '', key)
            delivery_instance = Delivery.objects.filter(name=name, type_d=value['type_d']).order_by('createdAt').first()

            if delivery_instance:
                delivery_instance.products_nums_on_list = value['products_nums_on_list']
                delivery_instance.lists = value['lists']
                delivery_instance.products_count = len(value['products_nums_on_list'])
                delivery_instance.save()
            else:
                try:
                    created_ins = Delivery(
                        id_wb='no',
                        name=name,
                        createdAt=value['createdAt'],
                        products_count=value['products_count'],
                        products_nums_on_list=value['products_nums_on_list'],
                        lists=value['lists'],
                        type=value['type'],
                        type_d=value['type_d'],
                        state=state_poster if value['type_d'] == 'posters' else state_badge,
                    )
                    created_ins.save()
                except Exception as ex:
                    logger.error(f"An error occurred while processing '{key}': {ex}")


def update_rows_delivery():
    # parser_wb_cards(api_key=api_key1, seller='Ярослав')
    # parser_wb_cards(api_key=api_key2, seller='Андрей')
    import os
    start_time = datetime.now()
    os.makedirs('files', exist_ok=True)
    data_list = []
    # try:
    #     seller = 'Ярослав'
    #     delivery_list = None
    #     delivery_list, seller = parser_wb_delivery(api_key=api_key1, seller=seller)
    #     data_list = result_list_data(delivery_list, api_key=api_key1, seller=seller)
    #
    #     seller = 'Андрей'
    #     delivery_list, seller = parser_wb_delivery(api_key=api_key2, seller=seller)
    #     data_list = result_list_data(delivery_list, data_list=data_list, api_key=api_key2, seller=seller)
    # except Exception as ex:
    #     with open('Ошибка парсинга WB.txt', 'w') as f:
    #         f.write(f'{ex}')
    try:
        create_rows_delivery(data_list)
    except Exception as ex:
        with open('Ошибка записи в базу.txt', 'w') as f:
            f.write(f'{ex}')
    logger.success(datetime.now() - start_time)


if __name__ == '__main__':
    update_rows_delivery()
