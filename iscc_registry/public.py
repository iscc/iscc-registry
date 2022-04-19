# -*- coding: utf-8 -*-
from django.contrib import admin
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicApp, PublicAdminSite
from iscc_registry.models import IsccIdModel, ChainModel


class IsccIdAdmin(PublicModelAdmin):
    list_display = ["admin_iscc_id", "admin_iscc_code", "owner", "admin_time", "revision"]
    list_filter = ["chain"]
    list_per_page = 20
    search_fields = [
        "iscc_id",
        "iscc_code",
    ]

    fieldsets = (
        (
            "Core Data",
            {
                "fields": (
                    "admin_iscc_id",
                    "admin_iscc_code",
                    "owner",
                    "revision",
                    "display_redirect",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": [
                    "meta_url",
                    "display_thumbnail",
                    "display_name",
                    "display_description",
                    "display_license",
                ],
            },
        ),
        (
            "Ledger Reference",
            {
                "fields": (
                    "chain",
                    "block_height",
                    "block_hash",
                    "tx_idx",
                    "tx_hash",
                    "display_ledger_url",
                )
            },
        ),
    )

    @admin.display(ordering="timestamp", description="timestamp")
    def admin_time(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(ordering="iscc_id", description="ISCC-ID")
    def admin_iscc_id(self, obj):
        return f"ISCC:{obj.iscc_id}"

    @admin.display(ordering="iscc_code", description="ISCC-CODE")
    def admin_iscc_code(self, obj):
        return f"ISCC:{obj.iscc_code}"

    def get_queryset(self, request):
        """Only list active and non-deleted ISCC-IDs"""
        qs = super().get_queryset(request)
        return qs.filter(active=True, deleted=False)


class ChainAdmin(PublicModelAdmin):
    list_display = ["chain", "name"]


public_app = PublicApp("iscc_registry", models=("IsccIdModel", "ChainModel"))
public_admin = PublicAdminSite("iscc_registry", public_app)
public_admin.enable_nav_sidebar = False
public_admin.register(IsccIdModel, IsccIdAdmin)
public_admin.register(ChainModel, ChainAdmin)
