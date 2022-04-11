from typing import Optional
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    """A user of the registry"""

    @classmethod
    def get_or_create(cls, wallet: str, group: str):
        """Get or reate user and add to group"""
        if group not in ("registrar", "declarer"):
            raise ValueError(f"invalid group {group}")
        try:
            user = cls.objects.get(username=wallet)
        except cls.DoesNotExist:
            user = cls.objects.create_user(username=wallet)
            group, group_created = Group.objects.get_or_create(name=group)
            user.groups.add(group)
        return user


class ChainModel(models.Model):
    """An observed Blockchain"""

    class Meta:
        verbose_name = "Chain"
        verbose_name_plural = "Chains"
        ordering = ["chain"]

    class Chain(models.IntegerChoices):
        PRIVATE = 0
        BITCOIN = 1
        ETHEREUM = 2
        POLYGON = 3

    chain = models.PositiveSmallIntegerField(
        primary_key=True,
        verbose_name="chain-id",
        choices=Chain.choices,
        help_text="Unique ID of blockchain network",
    )

    name = models.SlugField(
        verbose_name="name",
        max_length=32,
        help_text="Name of blockchain network",
    )

    url_template = models.CharField(
        verbose_name="url template",
        max_length=256,
        help_text="Template for explorer transaction url",
    )

    testnet_template = models.CharField(
        verbose_name="testnet template",
        max_length=256,
        help_text="Template for testnet explorer transaction url",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Chain(id={self.id}, name={self.name})"


class IsccIdModel(models.Model):
    """An ISCC-ID minted from a declaration."""

    class Meta:
        verbose_name = "ISCC-ID"
        verbose_name_plural = "ISCC-IDs"
        get_latest_by = "did"
        constraints = [
            models.UniqueConstraint(
                name="unique_active_iscc_id",
                fields=["iscc_id", "active"],
                condition=Q(active=True),
            )
        ]

    did = models.PositiveBigIntegerField(
        verbose_name="did",
        primary_key=True,
        help_text="Cross-Chain time-ordered unique Declaration-ID",
    )

    active = models.BooleanField(
        verbose_name="active", default=True, help_text="Whether the ISCC-ID is active"
    )

    iscc_id = models.CharField(
        verbose_name="ISCC-ID",
        max_length=32,
        null=False,
        help_text="ISCC-ID - digital asset identifier",
    )

    iscc_code = models.CharField(
        verbose_name="ISCC-CODE",
        max_length=96,
        null=False,
        help_text="An ISCC-CODE",
    )

    declarer = models.ForeignKey(
        "User",
        to_field="username",
        verbose_name="declarer",
        null=False,
        on_delete=models.PROTECT,
        related_name="declarations_from_user",
    )

    meta_url = models.URLField(
        verbose_name="meta_url",
        null=True,
        blank=True,
        default=None,
        help_text="URL for ISCC Metadata",
    )

    message = models.CharField(
        verbose_name="message",
        max_length=255,
        null=True,
        default=None,
        help_text="declaration processing instruction",
    )

    timestamp = models.DateTimeField(
        verbose_name="timestamp", null=False, help_text="Block time of declaration"
    )

    owner = models.ForeignKey(
        "User",
        verbose_name="owner",
        null=True,
        related_name="ownerships",
        on_delete=models.PROTECT,
        help_text="Wallet address of current owner",
    )

    chain = models.ForeignKey(
        "ChainModel",
        verbose_name="chain",
        null=False,
        on_delete=models.CASCADE,
        related_name="declarations_in_chain",
        help_text="Source chain of the declaration",
    )

    block_height = models.PositiveBigIntegerField(
        verbose_name="block height",
        help_text="N-th block on source ledger",
    )

    block_hash = models.CharField(
        verbose_name="block hash",
        max_length=255,
        help_text="Hash of block",
    )

    tx_idx = models.PositiveSmallIntegerField(
        verbose_name="transaction index",
        null=False,
        help_text="Index of transaction within block including the ISCC-DECLARATION",
    )

    tx_hash = models.CharField(
        verbose_name="transaction hash",
        null=False,
        blank=False,
        max_length=255,
        help_text="Hash of transaction that includes the ISCC-DECLARATION",
    )

    registrar = models.ForeignKey(
        "User",
        to_field="username",
        verbose_name="registrar",
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="registrations",
    )

    simhash = models.CharField(
        verbose_name="simhash", max_length=32, help_text="Simhash of ISCC-ID"
    )

    metadata = models.JSONField(
        verbose_name="metadata",
        null=True,
        blank=True,
        default=None,
        help_text="Linked ISCC Metadata",
    )

    frozen = models.BooleanField(
        verbose_name="frozen",
        default=False,
        help_text="Whether the ISCC-ID is updatable",
    )

    deleted = models.BooleanField(
        verbose_name="deleted",
        default=False,
        help_text="Whether the ISCC-ID has a `delete`-declaration",
    )

    revision = models.PositiveIntegerField(
        verbose_name="revision",
        default=0,
        help_text="Number of times updated",
    )

    @staticmethod
    def get_safe(iscc_id: str):
        """Ensure only the active and non-deleted ISCC-ID is returned"""
        return IsccIdModel.objects.get(iscc_id=iscc_id, active=True, deleted=False)

    def ancestor(self) -> Optional["IsccIdModel"]:
        """Return previous declaration for this ISCC-ID if existent"""
        return (
            IsccIdModel.objects.filter(iscc_id=self.iscc_id)
            .exclude(did=self.did)
            .only("did", "active")
            .order_by("did")
            .last()
        )

    def __str__(self):
        return f"ISCC:{self.iscc_id}"

    def __repr__(self):
        return f"IsccIDModel({self.did})"
