from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import *


def approve_course(modeladmin, request, queryset):
    queryset.exclude(published_at=None).update(approved_at=timezone.now())


def disapprove_course(modeladmin, request, queryset):
    queryset.update(approved_at=None)


approve_course.short_description = "Approve course"
disapprove_course.short_description = "Disapprove course"


class CourseListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("status")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "status"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("A", _("approved")),
            ("P", _("pending")),
            ("D", _("draft")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "A":
            return queryset.exclude(approved_at=None)
        if self.value() == "P":
            return queryset.exclude(published_at=None).filter(approved_at=None)
        if self.value() == "D":
            return queryset.filter(published_at=None)


class CourseAdmin(admin.ModelAdmin):
    actions = [approve_course, disapprove_course]
    list_filter = [CourseListFilter]


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseCategory)
admin.site.register(CourseTag)
admin.site.register(Topic)
admin.site.register(Lesson)
admin.site.register(Assignment)
admin.site.register(TopicItem)
