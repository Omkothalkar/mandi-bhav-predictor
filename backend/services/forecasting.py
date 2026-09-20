import os
import joblib
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime

class ForecastingService:
    @staticmethod
    def generate_forecast(latest_known_date_str: str, latest_known_price: float, horizon: int, strategy: str, crop: str = None, mandi: str = None):
        """
        Generates recursive forecast. 
        For naive strategy, it just repeats the latest known price.
        """
        forecasts = []
        latest_date = datetime.strptime(latest_known_date_str, '%Y-%m-%d')
        
        current_price = latest_known_price
        
        buffer = []
        model = None
        lag_1_arrivals = 0.0

        if strategy != 'naive' and crop and mandi:
            from backend.services.data_service import data_service
            hist_df = data_service.get_historical_prices(crop, mandi)
            if len(hist_df) >= 12:
                # Get last 12 prices
                buffer = hist_df['Modal_Price'].tail(12).tolist()
                lag_1_arrivals = hist_df['Arrivals'].iloc[-1]
                
                # Load model
                pair_name = f"{crop}_{mandi}".replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("/", "")
                model_path = os.path.join('models', f"{pair_name}_best_model.joblib")
                if os.path.exists(model_path):
                    try:
                        data = joblib.load(model_path)
                        model = data['model']
                    except Exception as e:
                        print(f"Error loading model {model_path}: {e}")
                        model = None
            
        for i in range(1, horizon + 1):
            forecast_date = latest_date + relativedelta(months=i)
            
            if strategy == 'naive' or model is None or len(buffer) < 12:
                pred_price = current_price
            else:
                # Calculate features dynamically
                features = {
                    'lag_1_price': buffer[-1],
                    'lag_2_price': buffer[-2],
                    'lag_3_price': buffer[-3],
                    'lag_6_price': buffer[-6],
                    'lag_12_price': buffer[-12],
                    'rolling_mean_3': np.mean(buffer[-3:]),
                    'rolling_std_3': np.std(buffer[-3:], ddof=1) if len(buffer[-3:]) > 1 else 0.0,
                    'rolling_mean_6': np.mean(buffer[-6:]),
                    'rolling_std_6': np.std(buffer[-6:], ddof=1) if len(buffer[-6:]) > 1 else 0.0,
                    'month_sin': np.sin(2 * np.pi * forecast_date.month / 12.0),
                    'month_cos': np.cos(2 * np.pi * forecast_date.month / 12.0),
                    'year': forecast_date.year,
                    'lag_1_arrivals': lag_1_arrivals
                }
                
                # Order must match exactly what was trained
                feature_order = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
                                 'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
                                 'month_sin', 'month_cos', 'year', 'lag_1_arrivals']
                                 
                X = pd.DataFrame([features], columns=feature_order)
                pred_price = float(model.predict(X)[0])
                
                # Append to buffer and pop oldest to maintain 12 prices
                buffer.append(pred_price)
                buffer.pop(0)
                
            forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'price': float(pred_price)
            })
            
            # For next iteration's naive fallback if needed
            current_price = pred_price
            
        return forecasts

forecasting_service = ForecastingService()
