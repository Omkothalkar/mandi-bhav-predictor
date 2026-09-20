import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.data_service import data_service
from backend.services.forecasting import forecasting_service
from backend.services.decision_engine import decision_engine

crop = "Wheat"
mandi = "Gujarat - Amreli - Amreli"

hist_df = data_service.get_historical_prices(crop, mandi)
print(f"Total historical records: {len(hist_df)}")

# From run_training.py, test set is 2016-07 to 2017-06 (12 months).
# But the backtest likely used the last 10 points. 
# "The same 10 eligible historical test origins from the backtest."
# A test origin T-1 means we forecast for T. 
# So we need to find the last 10 dates T in the dataset.
# Let's just take the last 10 points as T. The test origin will be T-1.

# Let's ensure chronological order
hist_df = hist_df.sort_values('Date').reset_index(drop=True)

test_indices = list(range(len(hist_df) - 10, len(hist_df)))

results = []

for idx in test_indices:
    t_row = hist_df.iloc[idx]
    t_minus_1_row = hist_df.iloc[idx-1]
    
    origin_date = t_minus_1_row['Date'].strftime('%Y-%m-%d')
    actual_t_minus_1 = t_minus_1_row['Modal_Price']
    actual_t = t_row['Modal_Price']
    
    # We need to simulate the prediction exactly as the backend would AT THE ORIGIN
    # We must only provide data up to T-1.
    # The forecasting service uses `data_service.get_historical_prices` inside.
    # To prevent leakage, forecasting_service loads data from data_service up to the full length! 
    # WAIT! forecasting_service.py line 26: `hist_df = data_service.get_historical_prices(crop, mandi)`
    # This reads the FULL dataset. So if we call it naively, it will use data from the future.
    # Actually, in a real backtest, we have to mock `data_service.get_historical_prices` to return data only up to T-1.
    
    # Let's mock it for the forecast call.
    original_get_hist = data_service.get_historical_prices
    
    def mocked_get_hist(c, m):
        df = original_get_hist(c, m)
        return df[df['Date'] <= t_minus_1_row['Date']]
        
    data_service.get_historical_prices = mocked_get_hist
    
    try:
        # Generate 1-step forecast for T
        forecasts = forecasting_service.generate_forecast(
            latest_known_date_str=origin_date,
            latest_known_price=actual_t_minus_1,
            horizon=1,
            strategy='hist_gradient_boosting',
            crop=crop,
            mandi=mandi
        )
        forecast_t = forecasts[0]['price']
    finally:
        data_service.get_historical_prices = original_get_hist

    # Percent changes
    fcst_pct_change = ((forecast_t - actual_t_minus_1) / actual_t_minus_1) * 100
    actual_pct_change = ((actual_t - actual_t_minus_1) / actual_t_minus_1) * 100
    
    # Decision Engine
    # Net return logic requires expected price per quintal. 
    # Current net return = Actual T-1 price * quantity - transport. 
    # Let's assume quantity 1, transport 0 for simplicity since they cancel out for percentages if 0.
    # Wait, in the backtest they must have used some defaults. The DE uses net returns. 
    # With 0 transport cost, net return == price.
    decision, reason = decision_engine.generate_decision(
        current_net_return=actual_t_minus_1,
        forecast_net_return=forecast_t,
        threshold_percent=2.0
    )
    
    # Forecast error (Bias: Forecast - Actual)
    error = forecast_t - actual_t
    
    # Realized return difference: Wait - Sell
    # If Sell: realized return is actual_t_minus_1
    # If Wait (for 1 step): realized return is actual_t
    realized_diff = actual_t - actual_t_minus_1
    
    results.append({
        'Test Date T': t_row['Date'].strftime('%Y-%m-%d'),
        'Actual T-1': actual_t_minus_1,
        'Forecast T': round(forecast_t, 2),
        'Actual T': actual_t,
        'Fcst % Change': round(fcst_pct_change, 2),
        'Act % Change': round(actual_pct_change, 2),
        'Decision': decision,
        'Error': round(error, 2),
        'Realized Diff (Wait - Sell)': realized_diff
    })

results_df = pd.DataFrame(results)
print("\nRaw Per-Origin Table:")
print(results_df.to_string())

# Aggregate diagnostics
mean_fcst_pct = results_df['Fcst % Change'].mean()
mean_act_pct = results_df['Act % Change'].mean()
median_fcst_pct = results_df['Fcst % Change'].median()
median_act_pct = results_df['Act % Change'].median()
mean_error = results_df['Error'].mean()
actual_inc_gt_2 = (results_df['Act % Change'] > 2.0).sum()
fcst_inc_gt_2 = (results_df['Fcst % Change'] > 2.0).sum()
fcst_dec = (results_df['Fcst % Change'] < 0.0).sum()

# Directional accuracy
results_df['Fcst Dir'] = np.sign(results_df['Fcst % Change'])
results_df['Act Dir'] = np.sign(results_df['Act % Change'])
dir_acc_count = (results_df['Fcst Dir'] == results_df['Act Dir']).sum()
dir_acc_pct = dir_acc_count / len(results_df) * 100

correlation = results_df['Fcst % Change'].corr(results_df['Act % Change'])

# Existing MAE and RMSE
mae = np.abs(results_df['Error']).mean()
rmse = np.sqrt((results_df['Error']**2).mean())

wait_count = (results_df['Decision'] == 'WAIT').sum()
sell_count = (results_df['Decision'] == 'SELL').sum()

sell_improved_by_waiting = ((results_df['Decision'] == 'SELL') & (results_df['Act % Change'] > 2.0)).sum()
pct_sell_improved = (sell_improved_by_waiting / sell_count * 100) if sell_count > 0 else 0

print("\nAggregate Diagnostics:")
print(f"1. Mean forecast % change: {mean_fcst_pct:.2f}%")
print(f"2. Mean actual % change: {mean_act_pct:.2f}%")
print(f"3. Median forecast % change: {median_fcst_pct:.2f}%")
print(f"4. Median actual % change: {median_act_pct:.2f}%")
print(f"5. Mean forecast error (bias): {mean_error:.2f}")
print(f"6. Actual price increases > 2%: {actual_inc_gt_2}")
print(f"7. Forecasts predicting > 2% increase: {fcst_inc_gt_2}")
print(f"8. Forecasts predicting decrease: {fcst_dec}")
print(f"9. Directional accuracy: {dir_acc_count}/{len(results_df)} ({dir_acc_pct:.1f}%)")
print(f"10. Correlation (Fcst vs Act % change): {correlation:.2f}")
print(f"11. MAE: {mae:.2f}, RMSE: {rmse:.2f}")
print(f"12. Decisions: WAIT={wait_count}, SELL={sell_count}")
print(f"13. % of SELL decisions where waiting improved return >2%: {pct_sell_improved:.1f}%")
