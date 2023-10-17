from datetime import timedelta

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
        cashed_data = cache.get('main', None)
        if cashed_data:
            return cashed_data
        locale_name = 'ru_RU.UTF-8'
        locale.setlocale(locale.LC_TIME, locale_name)
        current_datetime = timezone.now()
        current_year = current_datetime.year
        current_week_number = current_datetime.isocalendar()[1]
        # Отфильтруйте записи за текущий месяц
        current_month_appointments = Appointment.objects.filter(
            date__week=current_week_number,
            date__year=current_year,
            verified=True,
        )

        first_day_of_current_week = timezone.datetime.fromisocalendar(current_year, current_week_number, 1).date()

        user_works_day = {}
        uniq_user_id = current_month_appointments.values_list('user', flat=True).distinct()
        users = CustomUser.objects.filter(id__in=uniq_user_id)
        for user in users:
            hours_list = []
            for day in range(7):
                target_date = first_day_of_current_week + timedelta(days=day)
                hours_work = ""
                try:
                    apport = current_month_appointments.get(user=user, date=target_date)
                    hours_work = f'{apport.start_time.strftime("%H:%M")} - {apport.end_time.strftime("%H:%M")}'
                except Exception as ex:
                    pass
                hours_list.append(hours_work)
            user_works_day[user] = hours_list
        sorted_user_works_day = dict(sorted(user_works_day.items(), key=lambda x: x[0].username))
        context['days'] = [day.strftime("%d.%m") for day in
                           (first_day_of_current_week + timedelta(days=day) for day in range(7))]
        context['user_works_day'] = sorted_user_works_day

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
