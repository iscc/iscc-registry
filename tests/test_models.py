# -*- coding: utf-8 -*-
import pytest
from django.db import IntegrityError
import iscc_core as ic
from iscc_registry.exceptions import RegistrationError
from iscc_registry import models
from iscc_registry.transactions import register, rollback


wallet_a = "0x1ad91ee08f21be3de0ba2ba6918e714da6b45836"


def test_user_get_or_create(db):
    user = models.User.get_or_create(wallet=wallet_a, group="registrar")
    assert user.username == wallet_a
    assert user.groups.filter(name="registrar").exists()
    assert not user.groups.filter(name="declarer").exists()
    assert user.has_usable_password() is False
    user2 = models.User.get_or_create(wallet=wallet_a, group="registrar")
    assert user == user2


def test_register(db, dclr_a):
    iscc_id_obj = register(dclr_a)
    assert iscc_id_obj.iscc_id == "MIAKOP7RYAH5SVPN"
    with pytest.raises(RegistrationError):
        register(dclr_a)


def test_register_update(db, dclr_a, dclr_a_update):
    iid_a = register(dclr_a)
    assert iid_a.active is True
    assert iid_a.meta_url is None
    iid_b = register(dclr_a_update)
    iid_a.refresh_from_db()
    assert iid_a.active is False
    assert iid_a.iscc_id == iid_b.iscc_id
    assert iid_a.did != iid_b.did
    iid_query = models.IsccIdModel.objects.filter(iscc_id=iid_a.iscc_id)
    assert iid_query.count() == 2
    assert iid_query.latest().meta_url.startswith("ipfs://")


def test_iscc_id_model_ancestor(db, dclr_a, dclr_a_update):
    iid_a = register(dclr_a)
    iid_b = register(dclr_a_update)
    assert iid_b.ancestor().did == iid_a.did


def test_rollback(db, dclr_a, dclr_a_update):
    iid_a = register(dclr_a)
    assert iid_a.active is True
    iid_b = register(dclr_a_update)
    iid_a.refresh_from_db()
    assert iid_a.active is False
    rollback(iid_b.block_hash)
    assert models.IsccIdModel.objects.count() == 1
    iid_a.refresh_from_db()
    assert iid_a.active is True


def test_rollback_raises(db, dclr_a, dclr_a_update):
    with pytest.raises(IntegrityError):
        rollback(block_hash="a")


def test_declaration_freeze(db, dclr_a, dclr_a_update):
    dclr_a.message = "frz:"
    iscc_id_obj = register(dclr_a)
    assert iscc_id_obj.iscc_id == "MIAKOP7RYAH5SVPN"
    assert iscc_id_obj.frozen is True
    assert ic.Code(iscc_id_obj.iscc_id).explain == "ID-ETHEREUM-V0-64-a73ff1c00fd955ed"
    iscc_id_obj = register(dclr_a_update)
    assert iscc_id_obj.iscc_id == "MIA2OP7RYAH5SVPNAE"
    assert iscc_id_obj.frozen is False
    assert ic.Code(iscc_id_obj.iscc_id).explain == "ID-ETHEREUM-V0-72-a73ff1c00fd955ed-1"
