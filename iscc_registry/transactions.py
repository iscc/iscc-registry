from iscc_registry.exceptions import RegistrationError
from iscc_registry.schema import Declaration
from iscc_registry.models import DeclarationModel, BlockModel, User, IsccCodeModel, IsccIdModel
from django.db import transaction
import iscc_core as ic


@transaction.atomic
def register(d: Declaration) -> IsccIdModel:
    """Register an ISCC delcaration."""

    # check for duplicate
    if DeclarationModel.objects.filter(chain_id=d.chain_id, tx_hash=d.tx_hash).exists():
        raise RegistrationError(f"{d.chain_id}:{d.tx_hash} already registered")

    # initialize related objects

    block_obj, created = BlockModel.objects.select_for_update().get_or_create(
        chain_id=d.chain_id,
        block=d.block_id,
        hash=d.block_hash,
    )

    user_obj_declarer = User.get_or_create(wallet=d.declarer, group="declarer")

    user_obj_registrar = None
    if d.registrar:
        user_obj_registrar = User.get_or_create(wallet=d.declarer, group="registrar")

    iscc_code_obj, created = IsccCodeModel.objects.select_for_update().get_or_create(
        code=d.iscc_code
    )

    # Mint ISCC-ID
    uc = 0
    while True:
        candidate = d.iscc_id(uc=uc)
        iscc_id_obj, created = IsccIdModel.objects.select_for_update().get_or_create(
            iscc_id=candidate
        )

        if not created:
            # ISCC-ID exists. Check if we can update
            can_update = iscc_id_obj.owner.username == d.declarer
            can_update = can_update and iscc_id_obj.frozen is False and iscc_id_obj.deleted is False
            can_update = can_update and iscc_id_obj.iscc_code.code == d.iscc_code
            if not can_update:
                # Try the next ISCC-ID
                uc += 1
                continue

        dclr_obj = DeclarationModel.objects.create(
            time=d.time,
            chain_id=d.chain_id,
            block=block_obj,
            tx_idx=d.tx_idx,
            tx_hash=d.tx_hash,
            declarer=user_obj_declarer,
            message=d.message or None,
            meta_url=d.meta_url,
            registrar=user_obj_registrar,
        )
        dclr_obj.save()

        # ISCC-ID is unique. Mint/Update and return!
        iscc_id_obj.iscc_code = iscc_code_obj
        iscc_id_obj.simhash = ic.alg_simhash_from_iscc_id(iscc_id_obj.iscc_id, d.declarer)
        iscc_id_obj.owner = user_obj_declarer
        iscc_id_obj.frozen = d.freeze
        iscc_id_obj.deleted = d.delete
        # Update revision for existing ISCC-ID
        if not created:
            iscc_id_obj.revision = iscc_id_obj.revision + 1
        iscc_id_obj.save()
        iscc_id_obj.declarations.add(dclr_obj)
        iscc_id_obj.refresh_from_db()
        return iscc_id_obj
