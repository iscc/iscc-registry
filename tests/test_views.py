# -*- coding: utf-8 -*-


def test_view_index(client):
    response = client.get("/")
    assert b"Content Registry" in response.content
