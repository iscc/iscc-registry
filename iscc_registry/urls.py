from django.contrib import admin
from django.urls import path
from iscc_registry import views

urlpatterns = [
    path("", views.index),
    path("dashboard/", admin.site.urls),
]
