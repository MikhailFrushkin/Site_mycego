from collections import defaultdict
from datetime import datetime, timedelta
from pprint import pprint

from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from loguru import logger
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from completed_works.models import Standards, WorkRecord, WorkRecordQuantity, Delivery
from pay_sheet.models import PaySheetModel
from users.models import CustomUser
from work_schedule.models import Appointment, RequestsModel


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_staff']


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = CustomUser.objects.get(username=username)
            if check_password(password, user.password):
                return Response({'id': f'{user.id}',
                                 'role': f'{user.role}'})

        except Exception as ex:
            print(ex)
            return Response({'message': 'Неверный логин или пароль'}, status=HTTP_401_UNAUTHORIZED)


class AppointmentView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = int(request.data.get('user'))
        date = datetime.strptime(request.data.get('date'), "%Y-%m-%d").date()
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        try:
            row = Appointment.objects.get(user=user_id, date=date)
            return Response({'message': 'Запись существует'}, status=HTTP_401_UNAUTHORIZED)
        except Exception as ex:
            user = CustomUser.objects.get(pk=user_id)
            if user.status_work:
                row = Appointment(user=user, date=date, start_time=start_time_obj, end_time=end_time_obj)
                row.save()
                return JsonResponse({'message': f'Создана запись'}, status=200)
            return Response({'message': f'Не работает'}, status=403)

    def get(self, request):
        user_id = int(request.data.get('user'))
        user = CustomUser.objects.get(pk=user_id)

        try:
            current_date = datetime.now()
            current_week_number = current_date.isocalendar()[1]
            next_week_number = current_date.isocalendar()[1] + 1

            rows = Appointment.objects.filter(user=user, date__week=current_week_number) | \
                   Appointment.objects.filter(user=user, date__week=next_week_number)
            rows_data = [(i.date, i.start_time, i.end_time, i.verified, i.id) for i in rows.order_by('date')]
            return JsonResponse({'message': rows_data})
        except Exception as ex:
            pass


class AppointmentDelete(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = int(request.data.get('user'))
        user = CustomUser.objects.get(pk=user_id)
        appr_id = request.data.get('id')
        try:
            row = Appointment.objects.get(user=user, pk=appr_id)
            row.delete()
            return Response({'message': 'Запись удалена'})
        except Exception as ex:
            return Response({'message': f'Ошибка удаления'}, status=HTTP_401_UNAUTHORIZED)


class StandardsList(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(self):
        try:
            rows = Standards.objects.all()
            return JsonResponse({'data': [(i.id, i.name, i.delivery, i.standard) for i in rows]})
        except Exception as ex:
            return Response({'data': f'Ошибка обновления: {ex}'}, status=HTTP_401_UNAUTHORIZED)


class AddWorksList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        date = datetime.strptime(request.data.get('date'), "%Y-%m-%d").date()
        user_id = int(request.data.get('user'))
        delivery_id = request.data.get('delivery', None)
        try:
            user = CustomUser.objects.get(pk=user_id, status_work=True)
        except Exception as ex:
            return JsonResponse({'data': f'Не работает'}, status=403)
        works = request.data.get('works')
        comment = request.data.get('comment', None)
        print(request.data)
        logger.debug(delivery_id)
        if not delivery_id:
            try:
                logger.debug(user)
                logger.debug(date)
                logger.debug(comment)
                work_list = WorkRecord.objects.filter(user=user, date=date, delivery=None)
                if not work_list:
                    logger.success('Создается запись')
                    work_record = WorkRecord(user=user, date=date, comment=comment)
                    work_record.save()
                    for key, value in works.items():
                        standard = Standards.objects.get(id=key)
                        temp = WorkRecordQuantity(work_record=work_record, standard=standard, quantity=value)
                        temp.save()
                    return JsonResponse({'data': 'Отправлено!'}, status=200)
                else:
                    logger.debug(work_list)

                return JsonResponse({'data': f'Лист на эту дату существует'}, status=HTTP_401_UNAUTHORIZED)
            except Exception as ex:
                logger.error(ex)

        else:
            try:
                logger.debug(user)
                logger.debug(date)
                delivery = Delivery.objects.get(id=delivery_id)
                work_record = WorkRecord(user=user, date=date, delivery=delivery, comment=comment)
                work_record.save()
                for key, value in works.items():
                    standard = Standards.objects.get(id=key)
                    temp = WorkRecordQuantity(work_record=work_record, standard=standard, quantity=value)
                    temp.save()
                return JsonResponse({'data': 'Отправлено!'}, status=200)
            except Exception as ex:
                logger.error(ex)


class ViewWorks(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        from datetime import date, timedelta
        user_id = int(request.data.get('user'))
        user = CustomUser.objects.get(pk=user_id)
        try:
            today = date.today()
            start_of_week = today - timedelta(days=7)
            work_list = WorkRecord.objects.filter(user=user, delivery=None, date__gte=start_of_week)
            return JsonResponse({'data': [(i.id, i.date, i.is_checked) for i in work_list]})
        except Exception as ex:
            return Response({'data': 'Не найденно!'}, status=HTTP_401_UNAUTHORIZED)


class ViewDetailsWorks(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        work_id = int(request.data.get('work_id'))
        try:
            data = {}
            work_record = WorkRecord.objects.get(id=work_id)
            work_quantity = WorkRecordQuantity.objects.filter(work_record=work_record)
            for item in work_quantity:
                if item.quantity > 0:
                    data[item.standard.name] = item.quantity
            return JsonResponse({'data': data}, status=200)
        except Exception as ex:
            return Response({'data': 'Не найденно!'}, status=HTTP_401_UNAUTHORIZED)

    def post(self, request):
        work_id = int(request.data.get('work_id'))
        user_id = int(request.data.get('user_id'))
        user = CustomUser.objects.get(pk=user_id)
        try:
            work_list = WorkRecord.objects.get(id=work_id, user=user, is_checked=False)
            work_list.delete()
            return Response({'data': 'Удалена'}, status=200)
        except Exception as ex:
            return Response({'data': 'Ошибка'}, status=HTTP_401_UNAUTHORIZED)


class DeliveryView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(self):
        try:
            data = []
            current_datetime = timezone.now()
            start_date = current_datetime - timedelta(days=5)
            queryset = Delivery.objects.filter(
                Q(createdAt__gt=start_date) & ~Q(name__icontains='заказ') & ~Q(name__icontains='ЗАКАЗ') & ~Q(
                    name__icontains='Заказ')
            ).order_by('-createdAt')
            for item in queryset:
                data.append((item.id, item.name))
            print(len(queryset))
            return JsonResponse({'data': data}, status=200)
        except Exception as ex:
            return Response({'data': 'Не найденно!'}, status=HTTP_401_UNAUTHORIZED)


class DeliveryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = {}
            user_id = int(request.data.get('user_id'))
            user = CustomUser.objects.get(pk=user_id)
            current_datetime = timezone.now()
            start_date = current_datetime - timedelta(days=7)
            work_records = WorkRecord.objects.filter(user=user, date__gte=start_date).exclude(delivery__isnull=True)

            for record in work_records:
                temp_date = {}
                work_quantity = WorkRecordQuantity.objects.filter(work_record=record)
                for item in work_quantity:
                    if item.quantity > 0:
                        temp_date[item.standard.name] = item.quantity
                data[f'{record.date};{record.delivery};{record.id};{record.is_checked}'] = temp_date
            return JsonResponse({'data': data}, status=200)
        except Exception as ex:
            logger.error(ex)
            return Response({'data': 'Не найденно!'}, status=HTTP_401_UNAUTHORIZED)


class StatisticUserWork(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            date = datetime.now().date() - timedelta(days=7)
            user_id = int(request.data.get('user_id'))
            profile = get_object_or_404(CustomUser, pk=user_id)
            work_lists = WorkRecord.objects.filter(user=profile, delivery=None, date__gte=date)

            work_summary = defaultdict(int)

            for work_record in work_lists:
                work_quantities = WorkRecordQuantity.objects.filter(work_record=work_record)

                for work_quantity in work_quantities:
                    work_type = work_quantity.standard.name if work_quantity.standard else 'Удаленный вид работ'
                    work_summary[work_type] += work_quantity.quantity

            sorted_work_summary = dict(sorted(work_summary.items(), key=lambda item: item[1], reverse=True))

            context = {
                'profile': (profile.role.name, profile.avg_kf),
                'work_summary': sorted_work_summary,
            }
            return JsonResponse({'data': context}, status=200)
        except Exception as ex:
            logger.error(ex)
            return Response({'data': f'Ошибка! {ex}'}, status=HTTP_401_UNAUTHORIZED)


class RequestTg(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = int(request.data.get('user_id'))
        try:
            user = CustomUser.objects.get(pk=user_id)
            data = {}
            rows = RequestsModel.objects.filter(user=user)
            for row in rows:
                data[f'{row.type_request} - {row.created_at}'] = {
                    'comment': row.comment,
                    'result': row.result,
                    'comment_admin': row.comment_admin,
                }
            return JsonResponse({'data': data}, status=200)
        except Exception as ex:
            return Response({'data': 'Не найденно!'}, status=HTTP_401_UNAUTHORIZED)

    def post(self, request):
        logger.debug(request.data)
        type_r = request.data.get('type_r')
        comment = request.data.get('comment')
        user_id = int(request.data.get('user_id'))

        user = CustomUser.objects.get(pk=user_id)
        try:
            RequestsModel.objects.create(user=user, comment=comment, type_request=type_r)
            return Response({'data': 'Успешно'}, status=200)
        except Exception as ex:
            logger.error(ex)
            return Response({'data': 'Ошибка'}, status=HTTP_401_UNAUTHORIZED)
