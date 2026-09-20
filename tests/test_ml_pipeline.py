import sys
import requests

API_URL = "http://127.0.0.1:8000/api"

def run_test():
    case = {
        "crop": "Wheat",
        "state": "Gujarat",
        "district": "Amreli",
        "mandi": "Gujarat - Amreli - Amreli"
    }
    
    print(f"--- Validating ML Pipeline for: {case['crop']} | {case['mandi']} ---")
    
    # 1. Test Forecast Endpoint
    forecast_req = {
        "crop": case["crop"],
        "state": case["state"],
        "district": case["district"],
        "mandi": case["mandi"],
        "horizon": 3
    }
    resp = requests.post(f"{API_URL}/forecast", json=forecast_req)
    print("Forecast Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print("Strategy:", data.get('forecast_strategy'))
        prices = [f['price'] for f in data.get('forecasted_prices', [])]
        print("Forecasted Prices:", prices)
        
        # Verify the prices change (if ML model outputs vary over time, they should not be static, unlike naive)
        if prices[0] == prices[1] and prices[1] == prices[2]:
            print("NOTE: Prices are identical across months (model might predict a flat line)")
        else:
            print("SUCCESS: Prices are dynamically changing across months")
    else:
        print(resp.text)
        
    print("\n--- Testing Compare Endpoint ---")
    # 2. Test Compare Endpoint
    compare_req = {
        "crop": case["crop"],
        "quantity": 100,
        "quantity_unit": "tonnes",
        "transport_rate": 2.5,
        "mandis": [
            {
                "crop": case["crop"],
                "state": case["state"],
                "district": case["district"],
                "mandi": case["mandi"],
                "distance_km": 150
            }
        ]
    }
    resp = requests.post(f"{API_URL}/compare", json=compare_req)
    print("Compare Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        results = data.get('results', [])
        if results:
            res = results[0]
            print("Strategy:", res.get('forecast_strategy'))
            print("Forecast Price:", res.get('forecast_price'))
            print("Expected Net Return:", res.get('expected_net_return'))
            print("Transport Cost:", res.get('transport_cost'))
            print("Decision:", res.get('decision'))
            print("Decision Reason:", res.get('decision_reason'))
    else:
        print(resp.text)

if __name__ == '__main__':
    from backend.main import app
    import uvicorn
    import threading
    import time
    
    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
        
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3) # Wait for server to start
    run_test()
