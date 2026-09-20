import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.decision_engine import DecisionEngine

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_available_mandis():
    response = client.get("/api/available-mandis")
    assert response.status_code == 200
    data = response.json()
    assert "supported_mandis" in data
    # We should have our 5 mandis available
    assert len(data["supported_mandis"]) > 0
    mandi_names = [m["mandi"] for m in data["supported_mandis"]]
    assert "Gujarat - Vadodara(Baroda) - Vadodara" in mandi_names

def test_historical_prices():
    response = client.get("/api/historical-prices?crop=Rice&mandi=Gujarat - Vadodara(Baroda) - Vadodara")
    assert response.status_code == 200
    data = response.json()
    assert len(data["historical_prices"]) > 0
    assert data["metadata"]["limitation"] != ""

def test_historical_prices_not_found():
    response = client.get("/api/historical-prices?crop=Apple&mandi=Unknown")
    assert response.status_code == 404

def test_forecast_naive():
    req = {
        "crop": "Rice",
        "state": "Gujarat",
        "district": "Vadodara(Baroda)",
        "mandi": "Gujarat - Vadodara(Baroda) - Vadodara",
        "horizon": 3
    }
    response = client.post("/api/forecast", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_horizon"] == 3
    assert len(data["forecasted_prices"]) == 3
    assert data["forecast_strategy"] == "naive"
    
    # Check naive property: all forecast prices should equal the latest known price
    latest_price = data["latest_known_price"]
    for fp in data["forecasted_prices"]:
        assert fp["price"] == latest_price

def test_transport_cost_conversion():
    de = DecisionEngine()
    # 5 tonnes = 50 quintals. At 2 rs/km/quintal over 100 km -> 100 * 2 * 50 = 10000
    cost_tonnes = de.calculate_transport_cost(100, 2, 5, "tonnes")
    assert cost_tonnes == 10000.0
    
    # 50 quintals directly
    cost_quintals = de.calculate_transport_cost(100, 2, 50, "quintals")
    assert cost_quintals == 10000.0

def test_net_return():
    de = DecisionEngine()
    # price=2000, qty=10 tonnes (100 quintals) -> gross 200000
    gross, net = de.calculate_net_return(2000, 10, "tonnes", 10000)
    assert gross == 200000.0
    assert net == 190000.0

def test_decision_engine_rules():
    de = DecisionEngine()
    
    # net return improves from 100k to 105k (5%) -> WAIT
    decision, reason = de.generate_decision(100000, 105000, threshold_percent=2.0)
    assert decision == "WAIT"
    
    # net return improves from 100k to 101k (1%) -> SELL
    decision, reason = de.generate_decision(100000, 101000, threshold_percent=2.0)
    assert decision == "SELL"

def test_compare_endpoint():
    req = {
        "crop": "Rice",
        "quantity": 10,
        "quantity_unit": "tonnes",
        "transport_rate": 2.0,
        "mandis": [
            {
                "crop": "Rice",
                "state": "Gujarat",
                "district": "Vadodara(Baroda)",
                "mandi": "Gujarat - Vadodara(Baroda) - Vadodara",
                "distance_km": 150
            }
        ]
    }
    response = client.post("/api/compare", json=req)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    res = data["results"][0]
    
    assert "latest_known_historical_price" in res
    assert "expected_net_return" in res
    assert res["decision"] in ["SELL", "WAIT"]
