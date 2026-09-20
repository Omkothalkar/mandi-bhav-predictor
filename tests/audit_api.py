import sys
import json
import requests
import traceback

API_URL = "http://127.0.0.1:8000/api"

CASES = [
    {"crop": "Rice", "state": "Assam", "district": "Kamrup", "mandi": "Assam - Kamrup - P.O. Uparhali Guwahati"},
    {"crop": "Rice", "state": "Gujarat", "district": "Vadodara(Baroda)", "mandi": "Gujarat - Vadodara(Baroda) - Vadodara"},
    {"crop": "Rice", "state": "Karnataka", "district": "Kolar", "mandi": "Karnataka - Kolar - Chintamani"},
    {"crop": "Rice", "state": "Kerala", "district": "Alappuzha", "mandi": "Kerala - Alappuzha - Alappuzha"},
    {"crop": "Wheat", "state": "Gujarat", "district": "Junagarh", "mandi": "Gujarat - Junagarh - Mangrol"}
]

def run_tests():
    try:
        from backend.main import app
        import uvicorn
        import threading
        import time

        def start_server():
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(3) # Wait for server to start

        for i, case in enumerate(CASES):
            print(f"--- Testing Case {i+1}: {case['crop']} | {case['mandi']} ---")
            
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
                if len(prices) != 3:
                    print("ERROR: Did not return exactly 3 forecasts!")
            else:
                print(resp.text)
            
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
                    print("Transport Cost:", res.get('transport_cost'))
                    print("Expected Net Return:", res.get('expected_net_return'))
                    if res.get('transport_cost') != 375000:
                        print(f"ERROR: Transport cost is {res.get('transport_cost')} but expected 375000")
            else:
                print(resp.text)
            
            print()

    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    run_tests()
