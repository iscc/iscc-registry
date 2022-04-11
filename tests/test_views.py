# -*- coding: utf-8 -*-


def test_view_index(db, client):
    response = client.get("/", follow=True)
    assert b"Select ISCC-ID" in response.content
