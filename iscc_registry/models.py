from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse


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


class IsccCodeModel(models.Model):
    class Meta:
        verbose_name = "ISCC-CODE"
        verbose_name_plural = "ISCC-CODEs"

    code = models.CharField(
        verbose_name="ISCC-CODE",
        max_length=96,
        unique=True,
        db_index=True,
        help_text="An ISCC-CODE",
    )

    def __str__(self):
        return self.code


class IsccIdModel(models.Model):
    """An ISCC-ID minted from a declaration."""

    class Meta:
        verbose_name = "ISCC-ID"
        verbose_name_plural = "ISCC-IDs"

    iscc_id = models.CharField(
        verbose_name="ISCC-ID",
        max_length=32,
        help_text="ISCC-ID - digital asset identifier",
        unique=True,
        db_index=True,
    )

    simhash = models.CharField(
        verbose_name="simhash", max_length=32, help_text="Simhash decoded ISCC-ID"
    )

    iscc_code = models.ForeignKey(
        "IsccCodeModel",
        verbose_name="ISCC-CODE",
        null=True,
        default=None,
        related_name="iscc_ids",
        on_delete=models.PROTECT,
    )

    owner = models.ForeignKey(
        "User",
        verbose_name="owner",
        null=True,
        related_name="ownerships",
        on_delete=models.PROTECT,
        help_text="Wallet address of current owner",
    )

    # Optional fields

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

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse("admin:%s_%s_change" % info, args=(self.pk,))

    def __str__(self):
        return str(self.iscc_id)


class BlockModel(models.Model):
    class Meta:
        verbose_name = "Block"
        verbose_name_plural = "Blocks"
        # constraints = [models.UniqueConstraint(fields=("chain", "block"), name="unique_block")]

    chain = models.ForeignKey(
        "ChainModel",
        verbose_name="Chain",
        on_delete=models.CASCADE,
        help_text="Source Ledger/Blockchain",
        related_name="blocks",
    )

    block = models.PositiveBigIntegerField(
        verbose_name="block height",
        help_text="N-th block on source ledger",
    )

    hash = models.CharField(
        verbose_name="block hash",
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Hash of block",
    )

    def __str__(self):
        return f"{self.chain_id}-{self.block}-{self.hash[:6]}"


class DeclarationModel(models.Model):
    """A ledger entry that declares an ISCC-CODE"""

    class Meta:
        verbose_name = "Declaration"
        verbose_name_plural = "Declarations"
        get_latest_by = ["time", "chain_id", "block_id", "tx_idx"]
        constraints = [models.UniqueConstraint(fields=("chain", "tx_hash"), name="unique_tx")]

    time = models.DateTimeField(
        verbose_name="time", null=False, help_text="Block time of declaration"
    )

    chain = models.ForeignKey(
        "ChainModel",
        verbose_name="chain",
        null=False,
        on_delete=models.CASCADE,
        related_name="declarations_in_chain",
        help_text="Source chain of the declaration",
    )

    block = models.ForeignKey(
        "BlockModel",
        verbose_name="block",
        null=False,
        related_name="declarations_in_block",
        on_delete=models.CASCADE,
        help_text="Index of block that includes the ISCC-DECLARATION",
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
        unique=True,
        help_text="Hash of transaction that includes the ISCC-DECLARATION",
    )

    declarer = models.ForeignKey(
        "User",
        to_field="username",
        verbose_name="declarer",
        null=False,
        on_delete=models.PROTECT,
        related_name="declarations_from_user",
    )

    message = models.CharField(
        verbose_name="message",
        max_length=255,
        null=True,
        default=None,
        help_text="declaration processing instruction",
    )

    meta_url = models.URLField(
        verbose_name="meta_url",
        null=True,
        blank=True,
        default=None,
    )

    registrar = models.ForeignKey(
        "User",
        to_field="username",
        verbose_name="registrar",
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="declarations_from_registrar",
    )

    iscc_id = models.ForeignKey(
        "IsccIdModel",
        verbose_name="iscc-id",
        related_name="declarations",
        on_delete=models.PROTECT,
        null=True,
        default=None,
        help_text="ISCC-ID minted by this declaration",
    )

    metadata = models.JSONField(
        verbose_name="metadata",
        null=True,
        blank=True,
        default=None,
        help_text="Linked ISCC Metadata",
    )

    def __str__(self):
        return f"{self.chain.name}-{self.block_id}-{self.tx_hash[:6]}"

    def delete(self, using=None, keep_parents=False):
        pass
