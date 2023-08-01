from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(CourseCategory)
admin.site.register(CourseTag)
admin.site.register(Topic)
admin.site.register(Lesson)
admin.site.register(Assignment)
admin.site.register(TopicItem)
