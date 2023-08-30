from django.contrib import admin
from django.contrib.admin import *
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters


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
    list_filter = [CourseListFilter, "published_at", "approved_at"]

    change_form_template = "custom_change_form.html"

    def response_change(self, request, obj):
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)

        if "_approve_course" in request.POST or "_disapprove_course" in request.POST:
            # handle the action on your obj
            if "_approve_course" in request.POST:
                obj.approved_at = timezone.now()
                obj.save()
            if "_disapprove_course" in request.POST:
                obj.approved_at = None
                obj.save()

            ####################################
            redirect_url = reverse(
                "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                args=(pk_value,),
                current_app=self.admin_site.name,
            )
            redirect_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, redirect_url
            )
            return HttpResponseRedirect(redirect_url)
        else:
            return super().response_change(request, obj)


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseCategory)
admin.site.register(CourseTag)
admin.site.register(Topic)
admin.site.register(Lesson)
admin.site.register(Assignment)
admin.site.register(TopicItem)
