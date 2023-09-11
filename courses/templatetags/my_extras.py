import os
from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("custom_submit_line.html", takes_context=True)
def custom_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context["opts"]
    change = context["change"]
    is_popup = context["is_popup"]
    save_as = context["save_as"]
    ctx = {
        "opts": opts,
        "show_delete_link": (
            not is_popup
            and context["has_delete_permission"]
            and change
            and context.get("show_delete", True)
        ),
        "show_save_as_new": not is_popup and change and save_as,
        "show_save_and_add_another": (
            context["has_add_permission"]
            and not is_popup
            and (not save_as or context["add"])
        ),
        "show_save_and_continue": not is_popup and context["has_change_permission"],
        "is_popup": is_popup,
        "show_save": True,
        "preserved_filters": context.get("preserved_filters"),
    }
    if context.get("original") is not None:
        ctx["original"] = context["original"]
    return ctx


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


@register.filter
def get_continue_lesson_url(course):
    topic = course.topics.first()
    if topic is None:
        return "#"

    topic_item = topic.items.first()
    if topic_item is None:
        return "#"

    if topic_item.lesson:
        return reverse("courses:lesson_details", kwargs={"pk": topic_item.lesson.pk})
    elif topic_item.assignment:
        return reverse(
            "courses:assignment_details", kwargs={"pk": topic_item.assignment.pk}
        )
    elif topic_item.quiz:
        return reverse("courses:quiz_details", kwargs={"pk": topic_item.quiz.pk})
