import contextlib
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command

from utils.avg_kf_users import calculation_avg_kf
from utils.parser import update_rows_delivery


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(update_rows_delivery, 'interval', minutes=15, id='update_rows_delivery', replace_existing=True)
    scheduler.add_job(calculation_avg_kf, 'interval', minutes=10, id='calculation_avg_kf', replace_existing=True)

    print('Парсится')
    scheduler.start()


if __name__ == '__main__':
    start()