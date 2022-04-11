from django.contrib import admin
from django.urls import path
from iscc_registry.api import api
from iscc_registry.public import public_admin
from django.views.generic.base import RedirectView


urlpatterns = [
    path("dashboard/", admin.site.urls),
    path("api/", api.urls),
    path("registry/", public_admin.urls),
    path("", RedirectView.as_view(url="/registry/iscc_registry/isccidmodel/")),
]
