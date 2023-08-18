from django.db.models import F


def shift_items(sort_order, item, items):
    """Shift items to make room for a new item."""
    if sort_order > item.sort_order:
        items = items.filter(
            sort_order__gt=item.sort_order,
            sort_order__lte=sort_order,
        )
        items.update(sort_order=F("sort_order") - 1)

    elif sort_order < item.sort_order:
        items = items.filter(
            sort_order__lt=item.sort_order,
            sort_order__gte=sort_order,
        )
        items.update(sort_order=F("sort_order") + 1)
    item.sort_order = sort_order
    item.save()
