from dev.fake import Fake
from iscc_registry.schema import Forecast
from iscc_registry.transactions import register


def test_forecast_new(db, api_client):
    d = Fake().declaration
    f = Forecast(chain_id=d.chain_id, wallet=d.declarer, iscc_code=d.iscc_code)
    response = api_client.post("/forecast", json=f.dict())
    assert response.status_code == 200
    assert response.json() == {"iscc_id": "ISCC:MMAMRX3HC2SIFMUJ"}


def test_forecast_update(db, api_client):
    d = Fake().declaration
    iid_obj = register(d)
    f = Forecast(chain_id=d.chain_id, wallet=d.declarer, iscc_code=d.iscc_code)
    response = api_client.post("/forecast", json=f.dict())
    assert response.status_code == 200
    assert response.json()["iscc_id"] == f"ISCC:{iid_obj.iscc_id}"


def test_forecast_frozen(db, api_client):
    d = Fake().declaration
    iid_obj = register(d)
    iid_obj.frozen = True
    iid_obj.save()
    f = Forecast(chain_id=d.chain_id, wallet=d.declarer, iscc_code=d.iscc_code)
    response = api_client.post("/forecast", json=f.dict())
    assert response.status_code == 200
    assert f"ISCC:{iid_obj.iscc_id}" == "ISCC:MMAPRIKS27PZKNSI"
    assert response.json()["iscc_id"] == "ISCC:MMAPRIKS27PZKNSIAE"
