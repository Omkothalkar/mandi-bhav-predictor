import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.data_service import data_service
from scripts.run_training import create_features

crop = "Wheat"
mandi = "Gujarat - Amreli - Amreli"

# Load the full dataset to rebuild exactly as run_training.py did
data_path = 'data/processed/cleaned_dataset.csv'
df = pd.read_csv(data_path)
df['Reported Date'] = pd.to_datetime(df['Reported Date'])
df['YearMonth'] = df['Reported Date'].dt.to_period('M')

# Filter using the EXACT mandi string
pair_df = df[(df['Crop'] == crop) & (df['Mandi'] == mandi)].copy()

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

feat_df, _, _ = create_features(agg_df)

# Train mask: <= 2016-06-30
train_df = feat_df[feat_df.index <= pd.to_datetime('2016-06-30')]
# Validation/Test mask: > 2016-06-30
test_df = feat_df[feat_df.index >= pd.to_datetime('2016-07-01')]

print("=== 2. Distributions ===")
print("Train Target Stats:")
print(train_df['Modal Price (Rs./Quintal)'].describe())
print("\nTest Target Stats:")
print(test_df['Modal Price (Rs./Quintal)'].describe())

# Re-run 10-origin backtest for all models
hist_df = data_service.get_historical_prices(crop, mandi)
hist_df = hist_df.sort_values('Date').reset_index(drop=True)
test_indices = list(range(len(hist_df) - 10, len(hist_df)))

models = ['naive', 'linear_regression', 'random_forest', 'hist_gradient_boosting']

model_results = {m: [] for m in models}
feature_records = []

features = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
            'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
            'month_sin', 'month_cos', 'year', 'lag_1_arrivals']

X_train, y_train = train_df[features], train_df['Modal Price (Rs./Quintal)']

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

trained_models = {
    'linear_regression': LinearRegression().fit(X_train, y_train),
    'random_forest': RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train),
    'hist_gradient_boosting': HistGradientBoostingRegressor(random_state=42).fit(X_train, y_train)
}

for idx in test_indices:
    t_row = hist_df.iloc[idx]
    t_minus_1_row = hist_df.iloc[idx-1]
    
    actual_t_minus_1 = t_minus_1_row['Modal_Price']
    actual_t = t_row['Modal_Price']
    
    fcst_naive = actual_t_minus_1
    model_results['naive'].append({
        'Date': t_row['Date'], 'Actual': actual_t, 'Forecast': fcst_naive,
        'Fcst_Pct': 0.0,
        'Act_Pct': ((actual_t - actual_t_minus_1) / actual_t_minus_1) * 100,
        'Error': fcst_naive - actual_t
    })
    
    X_test_row = test_df.loc[t_row['Date'], features].to_frame().T
    
    for m_name, m_obj in trained_models.items():
        fcst = float(m_obj.predict(X_test_row)[0])
        model_results[m_name].append({
            'Date': t_row['Date'], 'Actual': actual_t, 'Forecast': fcst,
            'Fcst_Pct': ((fcst - actual_t_minus_1) / actual_t_minus_1) * 100,
            'Act_Pct': ((actual_t - actual_t_minus_1) / actual_t_minus_1) * 100,
            'Error': fcst - actual_t
        })
        
        if m_name == 'hist_gradient_boosting':
            feature_records.append(X_test_row.iloc[0].to_dict())

print("\n=== 5. Candidate ML Model Comparison ===")
for m_name in models:
    df_res = pd.DataFrame(model_results[m_name])
    mae = np.abs(df_res['Error']).mean()
    rmse = np.sqrt((df_res['Error']**2).mean())
    df_res['Fcst_Dir'] = np.sign(df_res['Fcst_Pct'])
    df_res['Act_Dir'] = np.sign(df_res['Act_Pct'])
    # Correct dir_acc calculation: naive is 0, so it matches 0 which only happens if actual_t == actual_t_minus_1
    dir_acc = (df_res['Fcst_Dir'] == df_res['Act_Dir']).mean() * 100
    bias = df_res['Error'].mean()
    
    print(f"\nModel: {m_name}")
    print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, Bias: {bias:.2f}, Dir Acc: {dir_acc:.1f}%")
    print("Forecast Pct Change Summary:")
    print(df_res['Fcst_Pct'].describe())
    
print("\n=== 3. Feature Distributions ===")
print("Train Features Summary (Subset):")
print(X_train[['lag_1_price', 'rolling_mean_3', 'rolling_std_3']].describe())
print("\nInference Features Summary (Subset):")
inf_feat_df = pd.DataFrame(feature_records)
print(inf_feat_df[['lag_1_price', 'rolling_mean_3', 'rolling_std_3']].describe())

print("\n=== Prediction vs Target Distribution ===")
hgb_df = pd.DataFrame(model_results['hist_gradient_boosting'])
print("HGB Forecasts Summary:")
print(hgb_df['Forecast'].describe())
