import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.decision_engine import decision_engine

def run_diagnostic():
    data_path = 'data/processed/cleaned_dataset.csv'
    model_path = 'models/Wheat_Gujarat___Amreli___Amreli_best_model.joblib'
    
    # 1. Load Data
    df = pd.read_csv(data_path)
    df['Reported Date'] = pd.to_datetime(df['Reported Date'])
    df['YearMonth'] = df['Reported Date'].dt.to_period('M')
    
    pair = {'Crop': 'Wheat', 'State Name': 'Gujarat', 'District Name': 'Amreli', 'Mandi': 'Gujarat - Amreli - Amreli'}
    pair_df = df[(df['Crop'] == pair['Crop']) & (df['Mandi'] == pair['Mandi'])].copy()
    
    agg_df = pair_df.groupby('YearMonth').agg(
        Modal_Price=('Modal Price (Rs./Quintal)', 'median'),
        Arrivals=('Arrivals (Tonnes)', 'sum')
    ).reset_index()
    
    full_range = pd.period_range(start=agg_df['YearMonth'].min(), end=agg_df['YearMonth'].max(), freq='M')
    agg_df = agg_df.set_index('YearMonth').reindex(full_range).rename_axis('YearMonth').reset_index()
    agg_df['Modal_Price'] = agg_df['Modal_Price'].ffill()
    agg_df['Arrivals'] = agg_df['Arrivals'].ffill()
    agg_df['Date'] = agg_df['YearMonth'].dt.to_timestamp()
    agg_df = agg_df.set_index('Date')
    
    test_mask = (agg_df.index >= pd.to_datetime('2016-07-01')) & (agg_df.index <= pd.to_datetime('2017-06-30'))
    test_dates = agg_df[test_mask].index
    
    model_data = joblib.load(model_path)
    model = model_data['model']
    
    records = []
    
    for t_date in test_dates:
        t_idx = agg_df.index.get_loc(t_date)
        if t_idx < 12 or t_idx + 2 >= len(agg_df):
            continue
            
        actual_t = agg_df.iloc[t_idx]['Modal_Price']
        
        hist_buffer = agg_df.iloc[t_idx-12:t_idx]['Modal_Price'].tolist()
        lag_1_arrivals = agg_df.iloc[t_idx-1]['Arrivals']
        t_minus_1_price = hist_buffer[-1]
        
        features = {
            'lag_1_price': hist_buffer[-1],
            'lag_2_price': hist_buffer[-2],
            'lag_3_price': hist_buffer[-3],
            'lag_6_price': hist_buffer[-6],
            'lag_12_price': hist_buffer[-12],
            'rolling_mean_3': np.mean(hist_buffer[-3:]),
            'rolling_std_3': np.std(hist_buffer[-3:], ddof=1) if len(hist_buffer[-3:]) > 1 else 0.0,
            'rolling_mean_6': np.mean(hist_buffer[-6:]),
            'rolling_std_6': np.std(hist_buffer[-6:], ddof=1) if len(hist_buffer[-6:]) > 1 else 0.0,
            'month_sin': np.sin(2 * np.pi * t_date.month / 12.0),
            'month_cos': np.cos(2 * np.pi * t_date.month / 12.0),
            'year': t_date.year,
            'lag_1_arrivals': lag_1_arrivals
        }
        
        feature_order = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
                         'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
                         'month_sin', 'month_cos', 'year', 'lag_1_arrivals']
                         
        X = pd.DataFrame([features], columns=feature_order)
        forecast_t = float(model.predict(X)[0])
        
        fcst_pct_change = ((forecast_t - t_minus_1_price) / t_minus_1_price) * 100 if t_minus_1_price > 0 else 0
        act_pct_change = ((actual_t - t_minus_1_price) / t_minus_1_price) * 100 if t_minus_1_price > 0 else 0
        forecast_error = forecast_t - actual_t
        
        quantity = 100
        quantity_unit = "tonnes"
        transport_rate = 2.5
        distance_km = 150
        transport_cost = decision_engine.calculate_transport_cost(distance_km, transport_rate, quantity, quantity_unit)
        
        _, current_net = decision_engine.calculate_net_return(t_minus_1_price, quantity, quantity_unit, transport_cost)
        _, forecast_net = decision_engine.calculate_net_return(forecast_t, quantity, quantity_unit, transport_cost)
        decision, _ = decision_engine.generate_decision(current_net, forecast_net)
        
        _, realized_wait_net = decision_engine.calculate_net_return(actual_t, quantity, quantity_unit, transport_cost)
        realized_return_diff = realized_wait_net - current_net
        realized_pct_improvement = (realized_return_diff / current_net) * 100 if current_net > 0 else 0
        
        records.append({
            'Test_Date_T': t_date.strftime('%Y-%m'),
            'Actual_T_Minus_1': t_minus_1_price,
            'Forecast_T': forecast_t,
            'Actual_T': actual_t,
            'Fcst_Pct_Change': fcst_pct_change,
            'Act_Pct_Change': act_pct_change,
            'Decision': decision,
            'Forecast_Error': forecast_error,
            'Realized_Diff_Wait_Sell': realized_return_diff,
            'Realized_Pct_Improvement': realized_pct_improvement
        })
        
    df_res = pd.DataFrame(records)
    
    print("--- Per-Origin Diagnostic Table ---")
    print(df_res[['Test_Date_T', 'Actual_T_Minus_1', 'Forecast_T', 'Actual_T', 'Fcst_Pct_Change', 'Act_Pct_Change', 'Decision', 'Forecast_Error', 'Realized_Diff_Wait_Sell']].to_string(index=False))
    print("\n")
    
    print("--- Aggregate Diagnostics ---")
    mean_fcst_pct = df_res['Fcst_Pct_Change'].mean()
    mean_act_pct = df_res['Act_Pct_Change'].mean()
    median_fcst_pct = df_res['Fcst_Pct_Change'].median()
    median_act_pct = df_res['Act_Pct_Change'].median()
    mean_error = df_res['Forecast_Error'].mean()
    
    act_inc_gt_2 = sum(df_res['Act_Pct_Change'] > 2.0)
    fcst_inc_gt_2 = sum(df_res['Fcst_Pct_Change'] > 2.0)
    fcst_dec = sum(df_res['Fcst_Pct_Change'] < 0)
    
    def same_sign(a, b):
        if a > 0 and b > 0: return True
        if a < 0 and b < 0: return True
        if a == 0 and b == 0: return True
        return False
        
    dir_acc = sum(same_sign(r['Fcst_Pct_Change'], r['Act_Pct_Change']) for _, r in df_res.iterrows())
    dir_acc_pct = (dir_acc / len(df_res)) * 100
    
    corr = df_res['Fcst_Pct_Change'].corr(df_res['Act_Pct_Change'])
    
    mae = mean_absolute_error(df_res['Actual_T'], df_res['Forecast_T'])
    rmse = root_mean_squared_error(df_res['Actual_T'], df_res['Forecast_T'])
    
    num_wait = sum(df_res['Decision'] == 'WAIT')
    num_sell = sum(df_res['Decision'] == 'SELL')
    
    sell_failure = sum((df_res['Decision'] == 'SELL') & (df_res['Realized_Pct_Improvement'] > 2.0))
    sell_failure_pct = (sell_failure / num_sell * 100) if num_sell > 0 else 0

    print(f"1. Mean forecast percentage change: {mean_fcst_pct:.2f}%")
    print(f"2. Mean actual percentage change: {mean_act_pct:.2f}%")
    print(f"3. Median forecast percentage change: {median_fcst_pct:.2f}%")
    print(f"4. Median actual percentage change: {median_act_pct:.2f}%")
    print(f"5. Mean forecast error (Bias): {mean_error:.2f}")
    print(f"6. Number of actual price increases > 2%: {act_inc_gt_2}")
    print(f"7. Number of forecasts predicting an increase > 2%: {fcst_inc_gt_2}")
    print(f"8. Number of forecasts predicting a decrease: {fcst_dec}")
    print(f"9. Directional accuracy: {dir_acc}/{len(df_res)} ({dir_acc_pct:.1f}%)")
    print(f"10. Correlation (forecast change vs actual change): {corr:.3f}")
    print(f"11. Existing MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    print(f"12. WAIT/SELL counts: WAIT={num_wait}, SELL={num_sell}")
    print(f"13. Percentage of SELL decisions where waiting actually improved realized return by >2%: {sell_failure_pct:.1f}% ({sell_failure}/{num_sell})")

if __name__ == '__main__':
    run_diagnostic()
