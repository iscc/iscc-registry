from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from iscc_registry import models
from django.db.models.expressions import F

admin.site.register(models.User, UserAdmin)


@admin.register(models.ChainModel)
class ChainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url_template")


@admin.register(models.IsccCodeModel)
class IsccCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.IsccIdModel)
class IsccIDAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 20
    # list_filter = [
    #     "chain",
    # ]
    search_fields = [
        "=iscc_id",
        "@iscc_code",
    ]
    list_display = [
        "iscc_id",
        "iscc_code",
        "declarer",
        "revision",
    ]

    # odering = ("-timestamp",)


@admin.register(models.BlockModel)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("chain", "block_height", "block_hash")
    list_filter = ("chain",)


@admin.register(models.DeclarationModel)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "iscc_id", "get_chain", "block", "tx_hash", "tx_out_idx")

    formfield_overrides = {
        JSONField: {
            "widget": JSONEditorWidget(width="54em", height="32em", options={"mode": "view"})
        },
    }

    def get_queryset(self, request):
        """Annotate with source chain"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_chain=F("block__chain__name"))
        return queryset

    @admin.display(description="Chain")
    def get_chain(self, obj):
        return obj._chain
