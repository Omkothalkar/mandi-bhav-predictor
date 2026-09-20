import os
import sys
import pandas as pd
import numpy as np
import warnings
from sklearn.ensemble import HistGradientBoostingRegressor

warnings.filterwarnings('ignore')

os.makedirs('results', exist_ok=True)

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
    return df.dropna()

print("Loading dataset...")
data_path = 'data/processed/cleaned_dataset.csv'
df = pd.read_csv(data_path)
df['Reported Date'] = pd.to_datetime(df['Reported Date'])
df['YearMonth'] = df['Reported Date'].dt.to_period('M')

print("Identifying eligible series...")
mandi_stats = df.groupby(['Crop', 'State Name', 'District Name', 'Mandi']).agg(
    unique_months=('YearMonth', 'nunique'),
    obs_count=('Reported Date', 'count')
).reset_index()

total_series = len(mandi_stats)
eligible_stats = mandi_stats[mandi_stats['unique_months'] >= 60].sort_values(by='obs_count', ascending=False)
eligible_series = eligible_stats.head(60).to_dict('records')

print(f"Total series: {total_series}, Eligible: {len(eligible_stats)}, Sampled for test: {len(eligible_series)}")

features = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
            'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
            'month_sin', 'month_cos', 'year', 'lag_1_arrivals']

results = []

count = 0
for pair in eligible_series:
    count += 1
    print(f"Processing {count}/{len(eligible_series)}: {pair['Crop']} in {pair['Mandi']}...")
    
    pair_df = df[(df['Crop'] == pair['Crop']) & (df['Mandi'] == pair['Mandi'])].copy()
    
    agg_df = pair_df.groupby('YearMonth').agg(
        Modal_Price=('Modal Price (Rs./Quintal)', 'median'),
        Arrivals=('Arrivals (Tonnes)', 'sum')
    ).reset_index()
    
    if agg_df.empty or pd.isna(agg_df['YearMonth'].min()):
        continue
        
    full_range = pd.period_range(start=agg_df['YearMonth'].min(), end=agg_df['YearMonth'].max(), freq='M')
    agg_df = agg_df.set_index('YearMonth').reindex(full_range).rename_axis('YearMonth').reset_index()
    agg_df['Modal_Price'] = agg_df['Modal_Price'].ffill()
    agg_df['Arrivals'] = agg_df['Arrivals'].ffill()
    agg_df['Date'] = agg_df['YearMonth'].dt.to_timestamp()
    agg_df = agg_df.set_index('Date')
    agg_df = agg_df.rename(columns={'Modal_Price': 'Modal Price (Rs./Quintal)', 'Arrivals': 'Arrivals (Tonnes)'})
    
    feat_df = create_features(agg_df)
    
    if len(feat_df) < 24:
        continue
        
    feat_df['target_absolute'] = feat_df['Modal Price (Rs./Quintal)']
    feat_df['target_diff'] = feat_df['Modal Price (Rs./Quintal)'] - feat_df['lag_1_price']
    feat_df['target_pct'] = (feat_df['Modal Price (Rs./Quintal)'] - feat_df['lag_1_price']) / feat_df['lag_1_price']
    
    train_df = feat_df[feat_df.index <= pd.to_datetime('2016-06-30')]
    test_df = feat_df[feat_df.index >= pd.to_datetime('2016-07-01')]
    
    if len(train_df) < 10 or len(test_df) < 3:
        continue
        
    train_max = train_df['target_absolute'].max()
    train_mean = train_df['target_absolute'].mean()
    train_std = train_df['target_absolute'].std()
    cv = (train_std / train_mean) if train_mean > 0 else 0
    volatility = 'high' if cv > 0.25 else ('medium' if cv > 0.15 else 'low')
    
    test_max = test_df['target_absolute'].max()
    is_ood = test_max > train_max
    
    X_train = train_df[features]
    
    models = {
        'absolute': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_absolute']),
        'diff': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_diff']),
        'pct': HistGradientBoostingRegressor(random_state=42).fit(X_train, train_df['target_pct'])
    }
    
    hist_df = agg_df.reset_index()
    test_indices = [i for i in range(len(hist_df)) if hist_df.iloc[i]['Date'] >= pd.to_datetime('2016-07-01')]
    test_indices = test_indices[:10]
    if len(test_indices) == 0:
        continue
        
    for idx in test_indices:
        t_minus_1_row = hist_df.iloc[idx-1]
        origin_date = t_minus_1_row['Date']
        
        buffer_prices = hist_df.iloc[:idx]['Modal Price (Rs./Quintal)'].tail(12).tolist()
        last_arrivals = hist_df.iloc[idx-1]['Arrivals (Tonnes)']
        
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
                    realized_return = actual_price if decision == "WAIT" else origin_price
                    wait_sell_difference = realized_return - origin_price
                    
                    results.append({
                        'crop': pair['Crop'],
                        'mandi': pair['Mandi'],
                        'volatility': volatility,
                        'is_ood': is_ood,
                        'origin': origin_date.strftime('%Y-%m-%d'),
                        'horizon': h,
                        'target_formulation': mode.upper(),
                        'actual_price': actual_price,
                        'previous_price': origin_price,
                        'predicted_price': pred_abs,
                        'predicted_pct_change': pred_pct_change,
                        'actual_pct_change': act_pct_change,
                        'absolute_error': np.abs(pred_abs - actual_price),
                        'error': pred_abs - actual_price,
                        'decision': decision,
                        'wait_sell_difference': wait_sell_difference
                    })

res_df = pd.DataFrame(results)
res_df.to_csv('results/global_target_validation.csv', index=False)
print("Finished evaluating. Saved to results/global_target_validation.csv")
