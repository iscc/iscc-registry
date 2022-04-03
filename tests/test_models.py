# -*- coding: utf-8 -*-
import pytest

from iscc_registry.exceptions import RegistrationError
from iscc_registry import models

wallet_a = "0x1ad91ee08f21be3de0ba2ba6918e714da6b45836"


def test_user_get_or_create(db):
    user = models.User.get_or_create(wallet=wallet_a, group="registrar")
    assert user.username == wallet_a
    assert user.groups.filter(name="registrar").exists()
    assert not user.groups.filter(name="declarer").exists()
    assert user.has_usable_password() is False
    user2 = models.User.get_or_create(wallet=wallet_a, group="registrar")
    assert user == user2


def test_declaration_register(db, dclr_a):
    iscc_id_obj = models.DeclarationModel.register(dclr_a)
    assert iscc_id_obj.iscc_id == "MIAKOP7RYAH5SVPN"
    with pytest.raises(RegistrationError):
        models.DeclarationModel.register(dclr_a)


def test_declaration_update(db, dclr_a, dclr_a_update):
    iscc_id_obj_a = models.DeclarationModel.register(dclr_a)
    assert iscc_id_obj_a.meta_url is None
    iscc_id_obj_b = models.DeclarationModel.register(dclr_a_update)
    assert iscc_id_obj_a == iscc_id_obj_b
    assert iscc_id_obj_b.iscc_id_declarations.count() == 2
    assert iscc_id_obj_b.meta_url.startswith("ipfs://")


def test_declaration_freeze(db, dclr_a):
    dclr_a.data = b"\x01".hex()
    iscc_id_obj = models.DeclarationModel.register(dclr_a)
    assert iscc_id_obj.iscc_id == "MIAKOP7RYAH5SVPN"
    assert iscc_id_obj.frozen is True
