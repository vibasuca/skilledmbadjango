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
