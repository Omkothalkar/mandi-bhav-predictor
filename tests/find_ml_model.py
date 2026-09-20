import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import joblib
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.run_training import create_features, safe_mape

def train_and_save_ml_model():
    data_path = 'data/processed/cleaned_dataset.csv'
    models_dir = 'models'
    df = pd.read_csv(data_path)
    df['Reported Date'] = pd.to_datetime(df['Reported Date'])
    df['YearMonth'] = df['Reported Date'].dt.to_period('M')
    
    # We found Wheat | Gujarat - Amreli - Amreli is an ML pair
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
    agg_df = agg_df.rename(columns={'Modal_Price': 'Modal Price (Rs./Quintal)', 'Arrivals': 'Arrivals (Tonnes)'})
    
    feat_df, orig_len, usab_len = create_features(agg_df)
    
    train_mask = feat_df.index <= pd.to_datetime('2016-06-30')
    test_mask = (feat_df.index >= pd.to_datetime('2016-07-01')) & (feat_df.index <= pd.to_datetime('2017-06-30'))
    
    train_df = feat_df[train_mask]
    test_df = feat_df[test_mask]
    
    features = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
               'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
               'month_sin', 'month_cos', 'year', 'lag_1_arrivals']
               
    X_train, y_train = train_df[features], train_df['Modal Price (Rs./Quintal)']
    X_test, y_test = test_df[features], test_df['Modal Price (Rs./Quintal)']
    
    baseline_preds = test_df['lag_1_price']
    
    models = {
        'Baseline_Naive': None,
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'HistGradientBoosting': HistGradientBoostingRegressor(random_state=42)
    }
    
    pair_metrics = {}
    
    best_model_name = None
    best_mae = float('inf')
    best_rmse = float('inf')
    best_model_obj = None
    
    for name, model in models.items():
        if name == 'Baseline_Naive':
            preds = baseline_preds.values
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
        mae = mean_absolute_error(y_test, preds)
        rmse = root_mean_squared_error(y_test, preds)
        mape = safe_mape(y_test, preds)
        
        pair_metrics[name] = {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}
        
        if mae < best_mae or (mae == best_mae and rmse < best_rmse):
            best_mae = mae
            best_rmse = rmse
            best_model_name = name
            best_model_obj = model
            
    print(f"Selected Model: {best_model_name}")
            
    pair_name = f"{pair['Crop']}_{pair['Mandi']}".replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("/", "")
    model_filename = os.path.join(models_dir, f"{pair_name}_best_model.joblib")
    
    strategy_map = {
        'Baseline_Naive': 'naive',
        'LinearRegression': 'linear_regression',
        'RandomForest': 'random_forest',
        'HistGradientBoosting': 'hist_gradient_boosting'
    }
    
    metadata = {
        'crop': pair['Crop'],
        'mandi': pair['Mandi'],
        'features': features,
        'model_name': best_model_name,
        'strategy': strategy_map[best_model_name],
        'metrics': pair_metrics[best_model_name]
    }
    joblib.dump({'model': best_model_obj, 'metadata': metadata}, model_filename)
    print(f"Saved to {model_filename}")

if __name__ == '__main__':
    train_and_save_ml_model()
