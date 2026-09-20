import os
import sys
import pandas as pd
import numpy as np
import warnings
from sklearn.ensemble import HistGradientBoostingRegressor

warnings.filterwarnings('ignore')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Feature Engineering
def create_features(df):
    df = df.copy()
    for lag in [1, 2, 3, 6, 12]:
        df[f'lag_{lag}_price'] = df['Modal Price (Rs./Quintal)'].shift(lag)
    df['lag_1_arrivals'] = df['Arrivals (Tonnes)'].shift(1)
    
    lag_1 = df['Modal Price (Rs./Quintal)'].shift(1)
    df['rolling_mean_3'] = lag_1.rolling(window=3).mean()
    df['rolling_std_3'] = lag_1.rolling(window=3).std()
    df['rolling_mean_6'] = lag_1.rolling(window=6).mean()
    df['rolling_std_6'] = lag_1.rolling(window=6).std()
    
    df['month'] = df.index.month
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12.0)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12.0)
    df['year'] = df.index.year
    df = df.dropna()
    return df

# Data Loading
crop = "Wheat"
mandi_full = "Gujarat - Amreli - Amreli"

data_path = 'data/processed/cleaned_dataset.csv'
df = pd.read_csv(data_path)
df['Reported Date'] = pd.to_datetime(df['Reported Date'])
df['YearMonth'] = df['Reported Date'].dt.to_period('M')

pair_df = df[(df['Crop'] == crop) & (df['Mandi'] == mandi_full)].copy()
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
agg_df = agg_df.rename(columns={'Modal_Price': 'Modal Price (Rs./Quintal)', 'Arrivals': 'Arrivals (Tonnes)'})

feat_df = create_features(agg_df)

feat_df['target_absolute'] = feat_df['Modal Price (Rs./Quintal)']
feat_df['target_diff'] = feat_df['Modal Price (Rs./Quintal)'] - feat_df['lag_1_price']
feat_df['target_pct'] = (feat_df['Modal Price (Rs./Quintal)'] - feat_df['lag_1_price']) / feat_df['lag_1_price']

train_df = feat_df[feat_df.index <= pd.to_datetime('2016-06-30')]
test_df = feat_df[feat_df.index >= pd.to_datetime('2016-07-01')]

print("=== Target Distributions (Train Set) ===")
targets = ['target_absolute', 'target_diff', 'target_pct']
for tgt in targets:
    print(f"\n{tgt}: Mean: {train_df[tgt].mean():.4f}, Median: {train_df[tgt].median():.4f}, Std: {train_df[tgt].std():.4f}, Min: {train_df[tgt].min():.4f}, Max: {train_df[tgt].max():.4f}")

features = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
            'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
            'month_sin', 'month_cos', 'year', 'lag_1_arrivals']

X_train = train_df[features]

models = {
    'absolute': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_absolute']),
    'diff': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_diff']),
    'pct': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_pct'])
}

hist_df = agg_df.reset_index()
test_indices = list(range(len(hist_df) - 10, len(hist_df)))

results_by_horizon = {h: [] for h in [1, 2, 3]}

for idx in test_indices:
    t_minus_1_row = hist_df.iloc[idx-1]
    
    buffer_prices = hist_df.iloc[:idx]['Modal Price (Rs./Quintal)'].tail(12).tolist()
    last_arrivals = hist_df.iloc[idx-1]['Arrivals (Tonnes)']
    origin_date = t_minus_1_row['Date']
    
    actuals = []
    for h in [1, 2, 3]:
        if idx - 1 + h < len(hist_df):
            actuals.append(hist_df.iloc[idx - 1 + h]['Modal Price (Rs./Quintal)'])
        else:
            actuals.append(np.nan)
            
    buffers = {
        'naive': list(buffer_prices), 'absolute': list(buffer_prices), 'diff': list(buffer_prices), 'pct': list(buffer_prices)
    }
    
    for h in [1, 2, 3]:
        fcst_date = origin_date + pd.DateOffset(months=h)
        for mode in ['naive', 'absolute', 'diff', 'pct']:
            buf = buffers[mode]
            prev_price = buf[-1]
            
            if mode == 'naive':
                pred_abs = prev_price
            else:
                X = pd.DataFrame([{
                    'lag_1_price': buf[-1], 'lag_2_price': buf[-2], 'lag_3_price': buf[-3],
                    'lag_6_price': buf[-6], 'lag_12_price': buf[-12],
                    'rolling_mean_3': np.mean(buf[-3:]), 'rolling_std_3': np.std(buf[-3:], ddof=1) if len(buf[-3:])>1 else 0,
                    'rolling_mean_6': np.mean(buf[-6:]), 'rolling_std_6': np.std(buf[-6:], ddof=1) if len(buf[-6:])>1 else 0,
                    'month_sin': np.sin(2 * np.pi * fcst_date.month / 12.0),
                    'month_cos': np.cos(2 * np.pi * fcst_date.month / 12.0),
                    'year': fcst_date.year, 'lag_1_arrivals': last_arrivals
                }])
                raw_pred = models[mode].predict(X)[0]
                
                if mode == 'absolute': pred_abs = raw_pred
                elif mode == 'diff': pred_abs = prev_price + raw_pred
                elif mode == 'pct': pred_abs = prev_price * (1 + raw_pred)
            
            buf.append(pred_abs)
            buf.pop(0)
            
            if not np.isnan(actuals[h-1]):
                actual_price = actuals[h-1]
                origin_price = buffer_prices[-1] 
                
                pred_pct_change = (pred_abs - origin_price) / origin_price * 100
                act_pct_change = (actual_price - origin_price) / origin_price * 100
                
                decision = "WAIT" if pred_pct_change > 2.0 else "SELL"
                
                # Realized return of the decision
                realized_return = actual_price if decision == "WAIT" else origin_price
                # Difference relative to forced SELL
                wait_sell_diff = realized_return - origin_price
                
                results_by_horizon[h].append({
                    'Model': mode,
                    'Origin': origin_date,
                    'Horizon': h,
                    'Prev_Price': origin_price,
                    'Pred_Price': pred_abs,
                    'Act_Price': actual_price,
                    'Pred_Pct': pred_pct_change,
                    'Act_Pct': act_pct_change,
                    'Error': pred_abs - actual_price,
                    'Decision': decision,
                    'Wait_Sell_Diff': wait_sell_diff
                })

metrics_table = []
for h in [1, 2, 3]:
    df_h = pd.DataFrame(results_by_horizon[h])
    for mode in ['naive', 'absolute', 'diff', 'pct']:
        m_df = df_h[df_h['Model'] == mode]
        if m_df.empty: continue
        
        mae = np.abs(m_df['Error']).mean()
        rmse = np.sqrt((m_df['Error']**2).mean())
        bias = m_df['Error'].mean()
        
        m_df['Pred_Dir'] = np.sign(m_df['Pred_Pct'])
        m_df['Act_Dir'] = np.sign(m_df['Act_Pct'])
        dir_acc = (m_df['Pred_Dir'] == m_df['Act_Dir']).mean() * 100
        
        min_pred_pct, max_pred_pct = m_df['Pred_Pct'].min(), m_df['Pred_Pct'].max()
        pred_gt_2 = (m_df['Pred_Pct'] > 2.0).sum()
        
        wait_count = (m_df['Decision'] == 'WAIT').sum()
        
        improved_cases = m_df[(m_df['Decision'] == 'WAIT') & (m_df['Act_Pct'] > 2.0)]
        pct_improved = (len(improved_cases) / wait_count * 100) if wait_count > 0 else 0.0
        
        avg_diff = m_df['Wait_Sell_Diff'].mean()
        
        metrics_table.append({
            'Target': mode.upper(), 'Horizon': h,
            'MAE': round(mae, 2), 'RMSE': round(rmse, 2), 'Bias': round(bias, 2),
            'Dir Acc %': round(dir_acc, 1),
            'Pred % Range': f"{min_pred_pct:.1f}% to {max_pred_pct:.1f}%",
            'Pred >2%': pred_gt_2, 'WAITs': wait_count,
            'WAITs Improved %': round(pct_improved, 1),
            'Avg Return Diff': round(avg_diff, 2)
        })

print("\n=== G. Final Comparison Table ===")
metrics_df = pd.DataFrame(metrics_table)
print(metrics_df.to_string(index=False))
