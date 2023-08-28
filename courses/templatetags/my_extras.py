import os
from django import template

register = template.Library()


@register.filter
def get_price_whole(value):
    if value is None:
        return "0"
    return str(value).split(".")[0]


@register.filter
def get_price_fraction(value):
    if value is None:
        return "00"
    return str(value).split(".")[1]


@register.filter
def get_timedelta_hours(value):
    total_seconds = value.total_seconds()
    total_hours = int(total_seconds // 3600)
    remaining_minutes = int((total_seconds % 3600) // 60)
    return total_hours


@register.filter
def get_timedelta_minutes(value):
    total_seconds = value.total_seconds()
    total_hours = int(total_seconds // 3600)
    remaining_minutes = int((total_seconds % 3600) // 60)
    return remaining_minutes


@register.filter
def get_filename(value):
    return os.path.basename(value)
