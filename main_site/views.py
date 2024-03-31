import collections
import datetime
from datetime import timedelta
from pprint import pprint

from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from loguru import logger
import locale

from completed_works.models import Standards
from main_site.models import Announcement, Category, GoodLink, Knowledge
from users.models import CustomUser
from work_schedule.models import Appointment


class MainPage(LoginRequiredMixin, TemplateView):
    template_name = 'main_page/main.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.datetime.now().today()
        day_first = today - datetime.timedelta(days=1)
        day_last = today + datetime.timedelta(days=5)

        user_appointments = (Appointment.objects.filter(date__range=[day_first, day_last])
                             .order_by('user__username', 'date'))

        set_date = user_appointments.values('date').order_by('date')

        user_schedule = {}

        for appointment in user_appointments:
            user = appointment.user
            date = appointment.date
            start_time = appointment.start_time
            end_time = appointment.end_time
            user_schedule[user] = {}

            if date not in user_schedule[user]:
                user_schedule[user][date] = {'start_time': None, 'end_time': None}

            user_schedule[user][date]['start_time'] = start_time
            user_schedule[user][date]['end_time'] = end_time

        # Заполнение дат, где записи отсутствуют, значениями None
        for user, dates in user_schedule.items():
            all_dates = set_date.values_list('date', flat=True)
            for date in all_dates:
                if date not in dates:
                    user_schedule[user][date] = {'start_time': None, 'end_time': None}
        context['user_schedule'] = user_schedule
        context['set_date'] = set_date

        # Добавляем объявления с пагинацией
        announcements = Announcement.objects.all().order_by('-is_pinned', '-date_created')
        paginator = Paginator(announcements, 10)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['announcements'] = page

        context.pop('view', None)
        cache.set('main', context, 600)
        return context


class KnowledgeCategory(LoginRequiredMixin, TemplateView):
    template_name = 'main_page/knowledge_category.html'
    login_url = '/users/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cashed_data = cache.get('know', None)
        if cashed_data:
            return cashed_data
        knows = Knowledge.objects.all()
        good_links = GoodLink.objects.all()

        category_dict = {item.category: [] for item in knows}
        good_links_dict = {item.category: [] for item in good_links}

        for item in knows:
            category_dict[item.category].append(item)

        for item in good_links:
            good_links_dict[item.category].append(item)

        standards = Standards.objects.all().order_by('standard')
        context['standards'] = standards
        context['good_links'] = good_links_dict
        context['category_dict'] = category_dict

        context.pop('view', None)
        cache.set('know', context, 600)
        return context
