from django.contrib.auth.models import AbstractUser, Group
from django.db import models, transaction
from django.urls import reverse
from iscc_registry.exceptions import RegistrationError
from iscc_registry.schema import Declaration
import iscc_core as ic


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

    name = models.SlugField()
    url_template = models.CharField(max_length=256, blank=True)

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

    iscc_code = models.ForeignKey(
        "IsccCodeModel",
        verbose_name="ISCC-CODE",
        null=False,
        blank=False,
        editable=False,
        related_name="iscc_ids",
        on_delete=models.PROTECT,
    )

    declarer = models.ForeignKey(
        "User",
        verbose_name="declarer",
        null=True,
        related_name="declarations",
        on_delete=models.PROTECT,
        help_text="PUBLIC-KEY or WALLET-ADDRESS of original DECLARING PARTY",
    )

    owner = models.ForeignKey(
        "User",
        verbose_name="owner",
        null=True,
        related_name="ownerships",
        on_delete=models.PROTECT,
        help_text="PUBLIC-KEY or WALLET-ADDRESS of current OWNER (after transfer)",
    )

    # Optional fields

    meta_url = models.URLField(
        verbose_name="metadata url",
        null=True,
        blank=True,
        default=None,
        help_text="URL with ISCC Metadata",
    )

    registrar = models.ForeignKey(
        User,
        verbose_name="registrar",
        null=True,
        on_delete=models.PROTECT,
        related_name="registrations",
        help_text="PUBLIC-KEY or WALLET-ADDRESS of REGISTRAR",
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

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse("admin:%s_%s_change" % info, args=(self.pk,))

    def __str__(self):
        return str(self.iscc_id)


class BlockModel(models.Model):
    class Meta:
        verbose_name = "Block"
        verbose_name_plural = "Blocks"

    chain = models.ForeignKey(
        "ChainModel",
        verbose_name="Chain",
        on_delete=models.CASCADE,
        help_text="Source Ledger/Blockchain",
        related_name="blocks",
    )

    block_height = models.PositiveBigIntegerField(
        verbose_name="block height",
        help_text="N-th block on source ledger",
    )

    block_hash = models.CharField(
        verbose_name="block hash",
        max_length=128,
        unique=True,
        db_index=True,
        help_text="Hash of block that includes the ISCC-DECLARATION",
    )

    def __str__(self):
        return self.block_hash


class DeclarationModel(models.Model):
    """A ledger entry that declares an ISCC-CODE"""

    class Meta:
        verbose_name = "Declaration"
        verbose_name_plural = "Declarations"
        get_latest_by = ["id"]
        ordering = ["id"]
        constraints = [models.UniqueConstraint(fields=("tx_hash", "tx_out_idx"), name="unique_tx")]

    id = models.PositiveBigIntegerField(
        verbose_name="id",
        primary_key=True,
        editable=False,
        help_text="Declaration-ID with block timestamp based flake (total ordering)",
    )

    iscc_id = models.ForeignKey(
        "IsccIdModel",
        verbose_name="iscc-id",
        related_name="iscc_id_declarations",
        on_delete=models.PROTECT,
        null=True,
        help_text="ISCC-ID minted by this declaration",
    )

    block = models.ForeignKey(
        "BlockModel",
        verbose_name="block",
        related_name="declarations_in_block",
        on_delete=models.CASCADE,
        null=True,
        help_text="The block that includes the ISCC-DECLARATION",
    )

    tx_hash = models.CharField(
        verbose_name="transaction hash",
        max_length=128,
        help_text="Hash of transaction that includes the ISCC-DECLARATION",
    )

    tx_out_idx = models.PositiveSmallIntegerField(
        verbose_name="transaction output",
        default=0,
        help_text="Output index that includes ISCC-DECLARATION (UTXO based chains)",
    )

    declaration = models.JSONField(
        verbose_name="declaration data",
        null=True,
        blank=True,
        default=None,
        help_text="Original declaration data",
    )

    def __str__(self):
        return ic.Flake.from_int(self.id).string

    @classmethod
    def register(cls, dclr: Declaration) -> IsccIdModel:
        """Register a new declaration"""

        # Check for duplicate registration
        if cls.objects.filter(tx_hash=dclr.tx_hash, tx_out_idx=dclr.tx_out_idx).exists():
            raise RegistrationError(f"{dclr.tx_hash}:{dclr.tx_out_idx} already registered")

        dclr_id = dclr.get_id()

        with transaction.atomic():
            # Create Declaration object
            dclr_obj = DeclarationModel.objects.create(
                id=dclr_id,
                tx_hash=dclr.tx_hash,
                tx_out_idx=dclr.tx_out_idx,
                declaration=dclr.dict(),
            )
            # Set block
            chain_obj, _ = ChainModel.objects.get_or_create(
                id=dclr.chain_id, defaults={"name": dclr.chain}
            )

            block_obj, _ = BlockModel.objects.get_or_create(
                block_hash=dclr.block_hash,
                block_height=dclr.block_height,
                chain=chain_obj,
            )
            block_obj.declarations_in_block.add(dclr_obj)

            # Create Users
            declarer_obj = User.get_or_create(wallet=dclr.declarer, group="declarer")
            registrar_obj = None
            if dclr.registrar:
                registrar_obj = User.get_or_create(wallet=dclr.declarer, group="registrar")

            iscc_code_obj, _ = IsccCodeModel.objects.get_or_create(code=dclr.iscc_code)
            # Mint ISCC-ID
            uc = 0
            while True:
                iscc_id = dclr.iscc_id(uc=uc)
                try:
                    iscc_id_obj = IsccIdModel.objects.get(iscc_id=iscc_id)
                except IsccIdModel.DoesNotExist:
                    # ISCC-ID is unique Mint and return
                    iscc_id_obj = IsccIdModel.objects.create(
                        iscc_id=iscc_id,
                        iscc_code=iscc_code_obj,
                        declarer=declarer_obj,
                        owner=declarer_obj,
                        meta_url=dclr.meta_url,
                        registrar=registrar_obj,
                        frozen=dclr.freeze,
                        deleted=dclr.delete,
                    )
                    dclr_obj.iscc_id = iscc_id_obj
                    dclr_obj.save()
                    return iscc_id_obj
                # ISCC-ID exists - check if we can update
                can_update = iscc_id_obj.owner.username == dclr.declarer
                can_update = (
                    can_update and iscc_id_obj.frozen is False and iscc_id_obj.deleted is False
                )
                can_update = can_update and iscc_id_obj.iscc_code.code == dclr.iscc_code
                if can_update:
                    iscc_id_obj.frozen = dclr.freeze
                    iscc_id_obj.deleted = dclr.delete
                    iscc_id_obj.meta_url = dclr.meta_url
                    iscc_id_obj.revision = iscc_id_obj.revision + 1
                    iscc_id_obj.registrar = registrar_obj
                    iscc_id_obj.iscc_id_declarations.add(dclr_obj)
                    iscc_id_obj.save()
                    return iscc_id_obj
                uc += 1

    def delete(self, using=None, keep_parents=False):
        pass
