from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "media_library"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="media_library/mediaManagement.html"),
        name="management",
    ),
    path("upload-media/", views.upload_media, name="upload_media"),
    path("list-media/", views.list_media, name="list_media"),
    path("update-media/<int:media_id>/", views.update_media, name="update_media"),
    path("read-media/<int:media_id>/", views.read_media, name="read_media"),
]
