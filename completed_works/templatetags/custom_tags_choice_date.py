from django import template
from django.utils.safestring import mark_safe
import datetime

from utils.utils import get_dates

register = template.Library()


@register.simple_tag
def choice_date(year=None, week=None, monday=None, sunday=None, download_excel=True):
    if not year:
        today = datetime.date.today()
        year = today.year
        week = today.isocalendar()[1]
    if not monday:
        try:
            monday, sunday = get_dates(int(year), int(week))
        except Exception as ex:
            print('ошибка', ex)
    html = f"""
        <div class="container text-center">
            <div class="row justify-content-md-center">
                <form method="get" class="custom-form">
                    <div class="form-group">
                        <span for="text_field_1" style="font-size: 14px;">Год:</span>
                        <input type="number"
                               min="2023" max="2050"
                               name="year"
                               placeholder="{year}"
                               class="narrower-input3"
                               value="{year}"
                               id="text_field_1">
                        <span for="text_field_2" style="font-size: 14px;">Неделя:</span>
                        <input type="number"
                               name="week"
                               min="1" max="53"
                               placeholder="{week}"
                               class="narrower-input3"
                               value="{week}"

                               id="text_field_2">

                        <button type="submit" class="btn-lg">Выбрать</button>
                        
                    </div>
                </form>
                <div>
                    <h4>
                        С {monday} по {sunday}
                    </h4>
                </div>
        """
    if download_excel:
        html += """
        <div>
                <a class="fw-4 fs-20" href="?download_excel=1&year={year}&week={week}">Скачать Excel</a>
                </div>
            </div>
        </div>
        """
    else:
        html += """
        </div>
        </div>"""
    return mark_safe(html)
