from django import template

register = template.Library()


@register.simple_tag
def get_date(dictionary, user, key):
    time = dictionary.get(user, {}).get(key, None)
    if time:
        start_time = time.get('start_time', None)
        end_time = time.get('end_time', None)
        if start_time and end_time:
            start_time_str = start_time.strftime('%H:%M')
            end_time_str = end_time.strftime('%H:%M')
            time_str = f"{start_time_str} - {end_time_str}"
        else:
            time_str = ''
    else:
        time_str = ''
    return time_str