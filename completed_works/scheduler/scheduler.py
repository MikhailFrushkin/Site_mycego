import contextlib
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command

from utils.parser import update_rows_delivery


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(update_rows_delivery, 'interval', minutes=50, id='update_rows_delivery', replace_existing=True)

    print('Парсится')
    scheduler.start()


if __name__ == '__main__':
    start()