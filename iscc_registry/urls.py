from django.contrib import admin
from django.urls import path
from iscc_registry import views
from iscc_registry.api import api

urlpatterns = [
    path("", views.index),
    path("api/", api.urls),
    path("dashboard/", admin.site.urls),
]
