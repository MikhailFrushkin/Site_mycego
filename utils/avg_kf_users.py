import os
from datetime import timedelta, datetime

from django.db.models import Sum, F, ExpressionWrapper, FloatField
from loguru import logger

from completed_works.models import WorkRecordQuantity
from users.models import CustomUser
from work_schedule.models import Appointment

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycego.settings')


def calculation_avg_kf():
    start_time = datetime.now()

    current_date = datetime.today().date()
    start_date = current_date - timedelta(days=7)

    users = CustomUser.objects.all()

    appointments = {}
    for appointment in Appointment.objects.filter(user__in=users, date__range=(start_date, current_date)):
        if appointment.user_id not in appointments:
            appointments[appointment.user_id] = {}
        exec_row = appointments[appointment.user_id].get(appointment.date, None)
        if exec_row:
            appointments[appointment.user_id][appointment.date] += appointment.duration.total_seconds() / 3600
        else:
            appointments[appointment.user_id][appointment.date] = appointment.duration.total_seconds() / 3600

    user_data_dict = {}
    for user in users:
        user_records = WorkRecordQuantity.objects.filter(
            work_record__user=user,
            work_record__delivery=None,
            work_record__date__gte=start_date
        ).order_by('work_record__user', 'work_record__date').values('work_record__id', 'work_record__date',
                                                                    'standard__name').annotate(
            total_quantity=Sum(F('quantity') * 1.0),
            total_standard=Sum(F('standard__standard') * 1.0)
        ).annotate(
            result=ExpressionWrapper(
                F('total_quantity') / F('total_standard'),
                output_field=FloatField()
            )
        )

        user_total_quantity = {}
        for record in user_records:
            date = record['work_record__date']
            record_id = record['work_record__id']
            result = record['result']
            hours = appointments.get(user.id, {}).get(date, None)
            if not hours:
                continue
            if date not in user_total_quantity:
                user_total_quantity[date] = [0, record_id]
            if result:
                user_total_quantity[date][0] += round((result / hours) * 100, 2)
        avg_value = None
        if user_total_quantity:
            user_data_dict[user] = user_total_quantity
            avg_value = round(sum(item[0] for item in user_total_quantity.values()) / len(user_total_quantity), 2)
        user.avg_kf = avg_value
        user.save()

    logger.success(datetime.now() - start_time)
