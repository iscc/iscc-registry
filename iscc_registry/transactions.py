from iscc_registry.exceptions import RegistrationError
from iscc_registry.schema import Declaration
from iscc_registry.models import User, IsccIdModel
from django.db import transaction
import iscc_core as ic


@transaction.atomic
def register(d: Declaration) -> IsccIdModel:
    """Register an ISCC delcaration."""

    # check for duplicate
    if IsccIdModel.objects.filter(did=d.did).exists():
        raise RegistrationError(f"Declaration {d.did} already registered")

    # initialize related objects
    user_obj_declarer = User.get_or_create(wallet=d.declarer, group="declarer")
    user_obj_registrar = None
    if d.registrar:
        user_obj_registrar = User.get_or_create(wallet=d.declarer, group="registrar")

    # Mint ISCC-ID
    uc = 0
    while True:
        candidate = d.get_iscc_id(uc=uc)
        iid_obj = (
            IsccIdModel.objects.filter(iscc_id=candidate)
            .only("iscc_code", "owner", "frozen", "deleted")
            .order_by("did")
            .last()
        )
        if iid_obj:
            # ISCC-ID exists. Check if we can update
            can_update = iid_obj.owner.username == d.declarer
            can_update = can_update and iid_obj.frozen is False and iid_obj.deleted is False
            can_update = can_update and iid_obj.iscc_code == d.iscc_code
            if not can_update:
                # Try the next ISCC-ID
                uc += 1
                continue
        break

    # Create new IsccIdModel entry for declaration event
    iid_obj = IsccIdModel(
        did=d.did,
        iscc_id=candidate,
        iscc_code=d.iscc_code,
        declarer=user_obj_declarer,
        meta_url=d.meta_url or None,
        message=d.message or None,
        timestamp=d.timestamp,
        owner=user_obj_declarer,
        chain_id=d.chain_id,
        block_height=d.block_height,
        block_hash=d.block_hash,
        tx_idx=d.tx_idx,
        tx_hash=d.tx_hash,
        registrar=user_obj_registrar,
        simhash=ic.alg_simhash_from_iscc_id(candidate, d.declarer),
        frozen=d.freeze,
        deleted=d.delete,
        revision=IsccIdModel.objects.filter(iscc_id=candidate).count() + 1,
    )
    iid_obj.save(force_insert=True)
    return iid_obj
