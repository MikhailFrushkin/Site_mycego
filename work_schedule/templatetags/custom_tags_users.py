from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def custom_dropdown(user_name, hours, users, num):
    if user_name[1]:
        mes = ''
    else:
        mes = '(не подтверждено)'
    html = f'<tr><th scope="row">{num}    {mes}</th>'

    for hour in hours:
        html += '<td><select class="form-select'
        if hour:
            html += ' bg-primary'
        else:
            html += ' bg-dark'
        html += ' w-auto text-white" aria-label="Запись">'

        if hour:
            html += f'<option selected>{user_name[0]}</option>'
        else:
            html += '<option selected>Нет</option>'

        html += f'<option style="color: #ffffff;">Нет</option>'

        for index, emp in enumerate(users, start=1):
            html += f'<option style="color: #ffffff;">{emp.username}</option>'

        html += '</select></td>'

    html += '<td><button class="btn btn-danger w-100 btn-clear" data-table-id="{{ key.1 }}" onclick="clearRow(this)">Очистить</button></td></tr>'

    return mark_safe(html)
