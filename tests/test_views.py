def test_view_index(client):
    response = client.get("/")
    assert b"Decentralized Content Registry" in response.content
