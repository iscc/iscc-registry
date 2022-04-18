from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from iscc_registry import models


admin.site.register(models.User, UserAdmin)


@admin.register(models.ChainModel)
class ChainAdmin(admin.ModelAdmin):

    list_display = ("chain_id", "name", "url_template", "testnet_template")
    list_editable = ("url_template", "testnet_template")

    @admin.display(description="chain-id")
    def chain_id(self, obj):
        return obj.chain


@admin.register(models.IsccIdModel)
class IsccIDAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = [
        "=iscc_id",
        "@iscc_code",
    ]
    list_display = [
        "did",
        "admin_iscc_id",
        "chain",
        "admin_iscc_code",
        "owner",
        "admin_time",
        "revision",
        "active",
    ]

    formfield_overrides = {
        JSONField: {
            "widget": JSONEditorWidget(width="53em", height="18em", options={"mode": "view"})
        },
    }

    @admin.display(ordering="timestamp", description="timestamp")
    def admin_time(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(ordering="iscc_id", description="iscc-id")
    def admin_iscc_id(self, obj):
        return f"ISCC:{obj.iscc_id}"

    @admin.display(ordering="iscc_code", description="iscc-code")
    def admin_iscc_code(self, obj):
        return f"ISCC:{obj.iscc_code}"
