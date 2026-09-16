from decimal import Decimal
import pytest
from app.pricing import PricingConfig, PricingEngine, PricingError, Tier

@pytest.fixture
def engine():
    tiers={"silver":Tier("Silver",Decimal("150"),18),"gold":Tier("Gold",Decimal("220"),12),"recliner":Tier("Recliner",Decimal("350"),0)}
    return PricingEngine(tiers, PricingConfig())

def test_non_member(engine):
    r=engine.calculate({"silver":2},False)
    assert r["ticket_subtotal"]==Decimal("300.00")
    assert r["festival_discount"]==Decimal("50.00")
    assert r["member_discount"]==Decimal("0.00")
    assert r["convenience_fee"]==Decimal("40.00")
    assert r["gst"]==Decimal("52.20")
    assert r["total"]==Decimal("342.20")

def test_member_discount_after_festival(engine):
    r=engine.calculate({"gold":2},True)
    assert r["member_discount"]==Decimal("39.00")
    assert r["total"]==Decimal("461.38")

def test_member_cap(engine):
    r=engine.calculate({"gold":6},True)
    assert r["member_discount"]==Decimal("100.00")

def test_multiple_tiers(engine):
    r=engine.calculate({"silver":1,"gold":1},False)
    assert r["quantity"]==2
    assert r["ticket_subtotal"]==Decimal("370.00")

def test_sold_out(engine):
    with pytest.raises(PricingError,match="sold out"):
        engine.calculate({"recliner":1})

def test_exceeds_inventory(engine):
    with pytest.raises(PricingError,match="remain"):
        engine.calculate({"silver":19})

def test_empty(engine):
    with pytest.raises(PricingError):
        engine.calculate({})

@pytest.mark.parametrize("qty", [0,-1,9])
def test_quantity_limits(engine,qty):
    with pytest.raises(PricingError):
        engine.calculate({"silver":qty})

def test_unknown_tier(engine):
    with pytest.raises(PricingError):
        engine.calculate({"VIP":1})


def test_api_tiers():
    from app.main import app
    client = app.test_client()
    response = client.get("/api/tiers")
    assert response.status_code == 200
    data = response.get_json()
    assert {item["name"] for item in data} == {"Silver", "Gold", "Recliner"}
    assert next(item for item in data if item["name"] == "Recliner")["available"] is False

def test_api_price():
    from app.main import app
    client = app.test_client()
    response = client.post("/api/price", json={"selections": {"Gold": 2}, "member": True})
    assert response.status_code == 200
    assert response.get_json()["total"] == "461.38"

def test_api_rejects_sold_out():
    from app.main import app
    client = app.test_client()
    response = client.post("/api/price", json={"selections": {"Recliner": 1}, "member": False})
    assert response.status_code == 400
    assert "sold out" in response.get_json()["error"].lower()
