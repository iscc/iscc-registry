from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from django_object_actions import DjangoObjectActions
from iscc_registry import models
from iscc_registry import tasks


@admin.register(models.User)
class IsccUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        original = super().get_fieldsets(request, obj)
        pi = ("Personal info", {"fields": ("name", "first_name", "last_name", "email", "url")})
        extended = (original[0], pi, original[2], original[3])
        return extended


@admin.register(models.ChainModel)
class ChainAdmin(admin.ModelAdmin):

    list_display = ("chain_id", "name", "url_template", "testnet_template")
    list_editable = ("url_template", "testnet_template")

    @admin.display(description="chain-id")
    def chain_id(self, obj):
        return obj.chain


@admin.register(models.IsccId)
class IsccIDAdmin(DjangoObjectActions, admin.ModelAdmin):
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

    def fetch_metdata(self, request, obj):
        result = tasks.fetch_metadata(did=obj.did)
        result(blocking=True)

    fetch_metdata.label = "Update"
    fetch_metdata.short_description = "Fetch metadata from Meta-URL"

    change_actions = ("fetch_metdata",)

    @admin.display(ordering="timestamp", description="timestamp")
    def admin_time(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(ordering="iscc_id", description="iscc-id")
    def admin_iscc_id(self, obj):
        return f"ISCC:{obj.iscc_id}"

    @admin.display(ordering="iscc_code", description="iscc-code")
    def admin_iscc_code(self, obj):
        return f"ISCC:{obj.iscc_code}"


@admin.register(models.Redact)
class RedactAdmin(admin.ModelAdmin):
    list_per_page = 15
    actions = None
    list_display = [
        "display_thumbnail",
        "iscc_id",
        "display_name",
        "display_description",
        "display_timestamp",
        "redacted",
    ]
    list_editable = ["redacted"]
    list_filter = ["redacted"]

    search_fields = ["iscc_id", "iscc_code", "metadata"]

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget(options={"mode": "view", "modes": ["view"]})},
    }

    readonly_fields = [
        "display_thumbnail_large",
        "did",
        "iscc_id",
        "iscc_code",
        "declarer",
        "registrar",
        "display_meta_url",
    ]

    fields = ["redacted"] + readonly_fields + ["metadata"]

    def get_queryset(self, request):
        """Only list active and non-deleted ISCC-IDs"""
        qs = super().get_queryset(request)
        return qs.filter(active=True, deleted=False)
