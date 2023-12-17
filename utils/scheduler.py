import asyncio
import contextlib
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command

from utils.avg_kf_users import calculation_avg_kf
from utils.parser import update_rows_delivery


def db_backup():
    with contextlib.suppress(Exception):
        call_command('dbbackup')


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    print('Создается backup')
    scheduler.add_job(db_backup, 'cron', hour=4, minute=0,
                      jobstore='default', id='day_backup', replace_existing=True)
    print('Парсится')
    scheduler.add_job(update_rows_delivery, 'interval', minutes=20, id='update_rows_delivery', replace_existing=True)

    print('Высчитывается кф')
    scheduler.add_job(calculation_avg_kf, 'interval', minutes=5, id='calculation_avg_kf', replace_existing=True)

    scheduler.start()

