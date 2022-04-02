# -*- coding: utf-8 -*-


def test_dashboard_login(client):
    response = client.get("/dashboard/", follow=True)
    assert b"Log in" in response.content
