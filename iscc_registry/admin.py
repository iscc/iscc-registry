from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from iscc_registry import models


admin.site.register(models.User, UserAdmin)


@admin.register(models.Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url_template")


@admin.register(models.IsccID)
class IsccIDAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 20
    list_filter = [
        "chain",
    ]
    search_fields = [
        "=iscc_id",
        "@iscc_code",
    ]
    list_display = [
        "iscc_id",
        "chain",
        "iscc_code",
        "declarer",
        "timestamp",
        "revision",
    ]

    odering = ("-timestamp",)
