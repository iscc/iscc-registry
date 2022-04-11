# -*- coding: utf-8 -*-
from django.contrib import admin
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicApp, PublicAdminSite
from iscc_registry.models import IsccIdModel, ChainModel


class IsccIdAdmin(PublicModelAdmin):
    list_display = ["iscc_id", "iscc_code", "owner", "admin_time", "revision"]
    list_filter = ["chain"]
    list_per_page = 20
    search_fields = [
        "iscc_id",
        "iscc_code",
    ]

    @admin.display(ordering="timestamp", description="timestamp")
    def admin_time(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")


class ChainAdmin(PublicModelAdmin):
    list_display = ["chain", "name"]


public_app = PublicApp("iscc_registry", models=("IsccIdModel", "ChainModel"))
public_admin = PublicAdminSite("iscc_registry", public_app)
public_admin.enable_nav_sidebar = False
public_admin.register(IsccIdModel, IsccIdAdmin)
public_admin.register(ChainModel, ChainAdmin)
