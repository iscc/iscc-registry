from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from iscc_registry import models
from django.db.models.expressions import F

admin.site.register(models.User, UserAdmin)


@admin.register(models.ChainModel)
class ChainAdmin(admin.ModelAdmin):

    list_display = ("chain_id", "name", "url_template", "testnet_template")
    list_editable = ("url_template", "testnet_template")

    @admin.display(description="chain-id")
    def chain_id(self, obj):
        return obj.chain


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
        "simhash",
        "iscc_code",
        "owner",
        "revision",
    ]


@admin.register(models.BlockModel)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("chain", "block", "hash")
    list_filter = ("chain",)


@admin.register(models.DeclarationModel)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "iscc_id",
        "admin_time",
        "chain",
        "block",
        "tx_idx",
        "declarer",
        "meta_url",
        "registrar",
    )

    @admin.display(ordering="time", description="time")
    def admin_time(self, obj):
        return obj.time.strftime("%Y-%m-%d %H:%M:%S")
