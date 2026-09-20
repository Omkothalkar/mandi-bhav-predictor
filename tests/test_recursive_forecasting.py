import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.services.forecasting import forecasting_service

class MockModel:
    def __init__(self):
        self.call_count = 0
        self.recorded_features = []
        
    def predict(self, X):
        self.call_count += 1
        self.recorded_features.append(X.copy())
        # Return a deterministic value so we can check if it propagates
        return [float(100 + self.call_count * 10)]

@pytest.fixture
def mock_hist_data():
    dates = pd.date_range(start='2022-01-01', periods=12, freq='ME')
    df = pd.DataFrame({
        'Date': dates,
        'Modal_Price': [20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0],
        'Arrivals': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    })
    return df

@patch('backend.services.forecasting.os.path.exists')
@patch('backend.services.forecasting.joblib.load')
@patch('backend.services.data_service.DataService.get_historical_prices')
def test_recursive_forecasting(mock_get_hist, mock_load, mock_exists, mock_hist_data):
    mock_get_hist.return_value = mock_hist_data
    mock_exists.return_value = True
    
    mock_model = MockModel()
    mock_load.return_value = {'model': mock_model}
    
    forecasts = forecasting_service.generate_forecast(
        latest_known_date_str="2022-12-31",
        latest_known_price=31.0,
        horizon=3,
        strategy="random_forest",
        crop="TestCrop",
        mandi="TestMandi"
    )
    
    assert len(forecasts) == 3
    assert mock_model.call_count == 3
    
    # Step 1:
    f1 = mock_model.recorded_features[0]
    # Check that lag_1_price is the last price in the buffer (31.0)
    assert f1['lag_1_price'].iloc[0] == 31.0
    assert f1['lag_2_price'].iloc[0] == 30.0
    
    # Check rolling stats (last 3: 29.0, 30.0, 31.0)
    expected_mean_3 = (29.0 + 30.0 + 31.0) / 3
    assert abs(f1['rolling_mean_3'].iloc[0] - expected_mean_3) < 1e-6
    
    # Step 1 prediction was 110.0 (100 + 1 * 10)
    assert forecasts[0]['price'] == 110.0
    
    # Step 2:
    f2 = mock_model.recorded_features[1]
    # Check that lag_1_price is now the PREDICTION from step 1
    assert f2['lag_1_price'].iloc[0] == 110.0
    # Check that lag_2_price shifted down to 31.0
    assert f2['lag_2_price'].iloc[0] == 31.0
    
    # Expected mean 3 for step 2 buffer [-3:]: 30.0, 31.0, 110.0
    expected_mean_3_step2 = (30.0 + 31.0 + 110.0) / 3
    assert abs(f2['rolling_mean_3'].iloc[0] - expected_mean_3_step2) < 1e-6
    
    # Step 3:
    f3 = mock_model.recorded_features[2]
    # Step 2 prediction was 120.0
    assert f3['lag_1_price'].iloc[0] == 120.0
    assert f3['lag_2_price'].iloc[0] == 110.0
    
    # Test column orders
    expected_cols = ['lag_1_price', 'lag_2_price', 'lag_3_price', 'lag_6_price', 'lag_12_price',
                     'rolling_mean_3', 'rolling_std_3', 'rolling_mean_6', 'rolling_std_6',
                     'month_sin', 'month_cos', 'year', 'lag_1_arrivals']
    assert list(f1.columns) == expected_cols
    assert list(f2.columns) == expected_cols
    assert list(f3.columns) == expected_cols
    
    # Arrivals should carry forward
    assert f1['lag_1_arrivals'].iloc[0] == 111.0
    assert f2['lag_1_arrivals'].iloc[0] == 111.0
    assert f3['lag_1_arrivals'].iloc[0] == 111.0
