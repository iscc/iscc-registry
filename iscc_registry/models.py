from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """A user of the registry"""

    pass


class Chain(models.Model):
    """An observed Blockchain"""

    name = models.SlugField()
    url_template = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Chain(id={self.id}, name={self.name})"

    class Meta:
        verbose_name = "Chain"
        verbose_name_plural = "Chains"


class IsccID(models.Model):
    """An ISCC-ID minted from a declaration."""

    # Minimum required declaration fields

    chain = models.ForeignKey(
        Chain,
        verbose_name="Chain",
        on_delete=models.CASCADE,
        help_text="Source Ledger/Blockchain",
    )

    iscc_id = models.CharField(
        verbose_name="ISCC-ID",
        max_length=32,
        help_text="ISCC-ID - digital asset identifier",
        unique=True,
    )

    iscc_code = models.CharField(
        verbose_name="ISCC-CODE",
        max_length=256,
        help_text="ISCC-CODE - digital asset descriptor",
    )

    declarer = models.ForeignKey(
        User,
        verbose_name="declarer",
        null=True,
        related_name="declarations",
        on_delete=models.SET_NULL,
        help_text="PUBLIC-KEY or WALLET-ADDRESS of DECLARING PARTY",
    )

    # Optional fields

    meta_url = models.URLField(
        verbose_name="metadata url",
        null=True,
        blank=True,
        default=None,
        help_text="URL with ISCC Metadata",
    )

    data = models.BinaryField(
        verbose_name="data",
        null=True,
        blank=True,
        default=None,
        help_text="Optional additional declaration data",
    )

    registrar = models.ForeignKey(
        User,
        verbose_name="registrar",
        null=True,
        on_delete=models.SET_NULL,
        related_name="registrations",
        help_text="PUBLIC-KEY or WALLET-ADDRESS of REGISTRAR",
    )

    metadata = models.JSONField(
        verbose_name="metadata",
        null=True,
        blank=True,
        default=None,
        help_text="ISCC Metadata",
    )

    # Ledger Reference Data

    block_height = models.PositiveBigIntegerField(
        verbose_name="block height",
        help_text="N-th block on source ledger",
    )

    block_hash = models.CharField(
        verbose_name="block hash",
        max_length=128,
        help_text="Hash of block that includes the ISCC-DECLARATION",
    )

    tx_hash = models.CharField(
        verbose_name="transaction hash",
        max_length=128,
        help_text="Hash of transaction that includes the ISCC-DECLARATION",
    )

    tx_out_idx = models.PositiveSmallIntegerField(
        verbose_name="transaction output",
        null=True,
        help_text="Output index that includes ISCC-DECLARATION (UTXO based chains)",
    )

    timestamp = models.DateTimeField(
        verbose_name="timestamp",
        help_text="Timestamp of block that includes the ISCC-DECLARATION",
    )

    revision = models.PositiveIntegerField(
        verbose_name="revision",
        default=0,
        help_text="Number of times updated",
    )

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse("admin:%s_%s_change" % info, args=(self.pk,))

    class Meta:
        verbose_name = "ISCC-ID"
        verbose_name_plural = "ISCC-IDs"
        indexes = [models.Index(fields=["timestamp"])]

    def __str__(self):
        return self.iscc_id
