from django.contrib import admin
from django.urls import path
from iscc_registry.api import api
from iscc_registry.public import public_admin
from iscc_registry import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path("dashboard/", admin.site.urls, name="dahsboard"),
    path("api/", api.urls, name="api"),
    path("registry/", public_admin.urls, name="registry"),
    path("<str:iscc_id>", views.resolver, name="resolver"),
    path("", RedirectView.as_view(url="/registry/iscc_registry/isccidmodel/"), name="index"),
]
