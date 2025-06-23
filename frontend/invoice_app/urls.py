from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload_view, name="upload"),
    path("viewer/", views.viewer, name="viewer"),
    path("chatbot/", views.chatbot, name="chatbot"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)