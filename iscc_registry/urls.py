from django.contrib import admin
from django.urls import path
from iscc_registry.api_v1 import api as api_v1
from iscc_registry.public import public_admin
from iscc_registry import views
from django.views.generic.base import RedirectView

index = RedirectView.as_view(url="/registry/iscc_registry/isccid/")

urlpatterns = [
    path("api/v1/", api_v1.urls, name="api-v1"),
    path("dashboard/", admin.site.urls, name="dashboard"),
    path("registry/", index),
    path("registry/iscc_registry/", index),
    path("registry/", public_admin.urls, name="registry"),
    path("<str:iscc_id>/", views.resolver, name="resolver"),
    path("", index, name="index"),
]
