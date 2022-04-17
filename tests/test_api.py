# -*- coding: utf-8 -*-
from dev.fake import Fake
from dev.load import load
from iscc_registry.models import IsccIdModel


def test_index(api_client):
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"docs": "/api/docs", "openapi": "/api/openapi.json", "version": "0.1.0"}


def test_head_auth_and_empty(db, api_client):
    resp = api_client.get("/head/1")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Unauthorized"}
    resp = api_client.get("/head/1", headers={"Authorization": "Bearer observer-token"})
    assert resp.status_code == 422
    assert resp.json() == {"message": "No registrations found for chain"}


def test_head(db, api_client):
    load(10)
    resp = api_client.get(f"/head/1", headers={"Authorization": "Bearer observer-token"})
    assert resp.status_code == 200
    assert resp.json() == {
        "block_hash": "0x8d005d0ba53ce166fcc9bf3a79e6d90ceb43c68929d6429bcfdcb0367a8ec52f",
        "block_height": 2590,
        "chain": 1,
        "timestamp": "2009-01-03T18:26:07Z",
        "tx_hash": "0x2cc0f859aa6524ab713b7e05ebe2136898c752051e01a934402d0baf878b9f6b",
        "tx_idx": 1402,
    }


def test_register(db, api_client):
    resp = api_client.post(
        "/register", json=Fake().declaration, headers={"Authorization": "Bearer observer-token"}
    )
    assert resp.status_code == 201
    assert resp.json() == {"did": 330445058337719994, "iscc_id": "ISCC:MMANWQAKQX42JUDB"}


def test_register_duplicate_fails(db, api_client):
    load(10)
    dec = Fake().declaration
    api_client.post("/register", json=dec, headers={"Authorization": "Bearer observer-token"})
    resp = api_client.post(
        "/register", json=dec, headers={"Authorization": "Bearer observer-token"}
    )
    assert resp.status_code == 422
    assert resp.json() == {"message": "Declaration 330445058337719994 already registered"}


def test_rollback(db, api_client):
    load(10)
    resp = api_client.post(
        "/rollback/0x17f922af7f6650d2aaf11f7e6a434f7218b4e50eeeab62adb19dae2245077965",
        headers={"Authorization": "Bearer observer-token"},
    )
    assert resp.status_code == 200
    assert IsccIdModel.objects.count() == 5
    assert resp.json() == {
        "block_hash": "0x37378e310269177c27f2c1e0a165ee7e84e83714a8fd279ef6b1de1b66b68980",
        "block_height": 837,
        "chain": 2,
        "timestamp": "2009-01-03T17:54:36Z",
        "tx_hash": "0x71eacd0549a3e80e966e12778c1745a79a6a5f92cca74147f6be1f723405095c",
        "tx_idx": 2213,
    }
    assert IsccIdModel.objects.count() == 5
    assert (
        IsccIdModel.objects.filter(
            block_hash="0x17f922af7f6650d2aaf11f7e6a434f7218b4e50eeeab62adb19dae2245077965"
        ).exists()
        is False
    )
