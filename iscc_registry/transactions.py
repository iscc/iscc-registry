from iscc_registry.exceptions import RegistrationError
from iscc_registry.schema import Declaration, Head
from iscc_registry.models import User, IsccId
from django.db import transaction, IntegrityError
import iscc_core as ic


@transaction.atomic
def register(d: Declaration) -> IsccId:
    """Register an ISCC delcaration."""

    # check for integirty
    qs = IsccId.objects.filter(did__gte=d.did, chain_id=d.chain_id).only("did").order_by("did")
    for obj in qs:
        if obj.did == d.did:
            raise RegistrationError(f"Declaration {d.did} already registered")
        raise RegistrationError(f"Found later declaration {obj.did} than {d.did}")

    # initialize related objects
    user_obj_declarer = User.get_or_create(wallet=d.declarer, group="declarer")
    user_obj_registrar = None
    if d.registrar:
        user_obj_registrar = User.get_or_create(wallet=d.declarer, group="registrar")

    # Mint ISCC-ID
    candidate = mint(d.iscc_code, d.chain_id, d.declarer)
    IsccId.objects.filter(iscc_id=candidate).update(active=False)

    # Create new IsccIdModel entry for declaration event
    new_iid_obj = IsccId(
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
        simhash=ic.alg_simhash_from_iscc_id(iscc_id=candidate, wallet=d.declarer),
        frozen=d.freeze,
        deleted=d.delete,
        revision=IsccId.objects.filter(iscc_id=candidate).count() + 1,
    )
    new_iid_obj.save(force_insert=True)
    return new_iid_obj


@transaction.atomic
def rollback(block_hash: str):
    """Reset event history to before `block_hash` in case of a fork."""
    start_obj = IsccId.objects.filter(block_hash=block_hash).order_by("did").first()
    if start_obj is None:
        raise IntegrityError(f"No declaration found for block {block_hash}")

    # Select events from all chains for backwards iteration to have consistent state
    stale_qs = IsccId.objects.filter(did__gte=start_obj.did).order_by("-did").only("did", "active")
    stale_qs.update(active=False)
    for stale_obj in stale_qs:
        anc = stale_obj.ancestor()
        if anc:
            anc.active = True
            anc.save()
        stale_obj.delete()

    new_head = IsccId.objects.filter(chain_id=start_obj.chain_id).order_by("did").last()
    return Head.from_orm(new_head)


def mint(iscc_code: str, chain_id: int, wallet: str) -> str:
    """
    Mint ISCC-ID according to Minting protocol based on the history of the registry.
    """
    uc = 0
    while True:
        candidate = ic.gen_iscc_id_v0(iscc_code, chain_id, wallet, uc=uc)["iscc"].lstrip("ISCC:")
        iid_obj = (
            IsccId.objects.filter(iscc_id=candidate)
            .only("iscc_code", "owner", "frozen", "deleted")
            .order_by("did")
            .last()
        )
        if iid_obj:
            # ISCC-ID exists. It should be active.
            if iid_obj.active is False:
                raise IntegrityError(f"Latest {iid_obj.iscc_id} is not active")
            # Check if we can update
            can_update = iid_obj.owner.username == wallet
            can_update = can_update and iid_obj.frozen is False and iid_obj.deleted is False
            can_update = can_update and iid_obj.iscc_code == iscc_code
            if not can_update:
                # Try the next ISCC-ID
                uc += 1
                continue
        return candidate
