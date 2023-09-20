import contextlib
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command


def db_backup():
    with contextlib.suppress(Exception):
        call_command('dbbackup')


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    # Установите желаемое время для выполнения резервного копирования базы данных
    backup_time = "04:00"  # Например, 4:00 утра

    # Запустите задачу каждый день в указанное время
    scheduler.add_job(db_backup, 'cron', hour=backup_time.split(':')[0], minute=backup_time.split(':')[1],
                      jobstore='default', id='day_backup', replace_existing=True)

    register_events(scheduler)
    print('Создался backup')
    scheduler.start()
