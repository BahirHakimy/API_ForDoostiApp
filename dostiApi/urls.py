from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("dostiApi/", include("dosti.urls")),
    path("chat/", include("chat.urls")),
    path("/", admin.site.urls),
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
