from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from utils.avg_kf_users import calculation_avg_kf
from utils.parser import update_rows_delivery


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(update_rows_delivery, 'interval', minutes=300, id='update_rows_delivery', replace_existing=True)
    scheduler.add_job(calculation_avg_kf, 'interval', minutes=150, id='calculation_avg_kf', replace_existing=True)

    print('Парсится')
    scheduler.start()


if __name__ == '__main__':
    start()