from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework import serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from completed_works.models import Standards, WorkRecord, WorkRecordQuantity
from users.models import CustomUser
from work_schedule.models import Appointment


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


class WorksList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            rows = Standards.objects.all()
            return JsonResponse({'data': [(i.id, i.name) for i in rows]})
        except Exception as ex:
            return Response({'data': f'Ошибка удаления'}, status=HTTP_401_UNAUTHORIZED)


class AddWorksList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        date = datetime.strptime(request.data.get('date'), "%Y-%m-%d").date()
        user_id = int(request.data.get('user'))
        try:
            user = CustomUser.objects.get(pk=user_id, status_work=True)
        except Exception as ex:
            return JsonResponse({'data': f'Не работает'}, status=403)
        works = request.data.get('works')
        try:
            work_list = WorkRecord.objects.get(user=user, date=date)
            return JsonResponse({'data': f'Лист на эту дату существует'}, status=HTTP_401_UNAUTHORIZED)
        except Exception as ex:
            work_record = WorkRecord(user=user, date=date)
            work_record.save()
            for key, value in works.items():
                standard = Standards.objects.get(id=key)
                temp = WorkRecordQuantity(work_record=work_record, standard=standard, quantity=value)
                temp.save()
            return JsonResponse({'data': 'Отправлено!'}, status=200)


class ViewWorks(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = int(request.data.get('user'))
        user = CustomUser.objects.get(pk=user_id)
        try:
            work_list = WorkRecord.objects.filter(user=user)
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