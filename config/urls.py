from django.contrib import admin
from django.urls import path, include

from config.settings import DEBUG

urlpatterns = [
    path("api/", include("api.urls")),
    path("", include("app.urls")),
]

if DEBUG:
    urlpatterns.append(path("admin/", admin.site.urls))
