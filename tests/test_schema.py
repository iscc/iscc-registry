# -*- coding: utf-8 -*-
import time

import pytest
from pydantic import ValidationError

from iscc_registry import schema


def test_schema_api():
    api_obj = schema.API()
    assert api_obj.dict() == {
        "docs": "/api/docs",
        "openapi": "/api/openapi.json",
        "version": "0.1.0",
    }


def test_schema_declaration(dclr_a):
    assert dclr_a.dict() == {
        "block_hash": "0x60735e41758bd8f411117ac7f20ef3779c35ab9c9c2e4f5c70c87d4d73979f05",
        "block_height": 14514543,
        "chain": "ethereum",
        "data": None,
        "declarer": "0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        "iscc_code": "KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI",
        "meta_url": None,
        "registrar": None,
        "timestamp": 1649008119.0,
        "tx_hash": "0xcade12c2cba31fbbfeddd1df932388dcd1c43fa346e233e34915dc3694546f3a",
        "tx_out_idx": 0,
    }


def test_declaration_raises():
    with pytest.raises(ValidationError):
        assert schema.Declaration(chain="ethereum")


def test_declaration_get_id(dclr_a):
    assert str(dclr_a.get_id()).startswith("108069396086")


def test_declaration_get_id_monotonic(dclr_a):
    id_a = dclr_a.get_id()
    id_b = dclr_a.get_id()
    assert id_a < id_b


def test_declaration_freeze_default_false(dclr_a):
    assert dclr_a.freeze is False


def test_declaration_delete_default_false(dclr_a):
    assert dclr_a.delete is False


def test_declaration_chain_id(dclr_a):
    assert dclr_a.chain_id == 2


def test_declaration_iscc_id(dclr_a):
    assert dclr_a.iscc_id() == "MIAKOP7RYAH5SVPN"
    assert dclr_a.iscc_id(uc=1) == "MIA2OP7RYAH5SVPNAE"
