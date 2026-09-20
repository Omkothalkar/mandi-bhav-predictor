import pandas as pd
import joblib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DataService:
    def __init__(self, data_path=None, models_dir=None):
        self.data_path = Path(data_path) if data_path else PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
        self.models_dir = Path(models_dir) if models_dir else PROJECT_ROOT / "models"
        self.df = None
        self.supported_pairs = []
        self._load_data()
        self._load_supported_mandis()

    def _load_data(self):
        if not self.data_path.is_file():
            raise FileNotFoundError(
                f"Data file not found at {self.data_path}. "
                "Generate it before starting the API with "
                "python scripts/prepare_deployment_data.py."
            )
        # Only loading essential columns to save memory
        self.df = pd.read_csv(self.data_path, usecols=['Reported Date', 'State Name', 'District Name', 'Mandi', 'Crop', 'Modal Price (Rs./Quintal)', 'Arrivals (Tonnes)'])
        self.df['Reported Date'] = pd.to_datetime(self.df['Reported Date'])
        
        # Aggregate to monthly level exactly as training phase did
        self.df['YearMonth'] = self.df['Reported Date'].dt.to_period('M')
        # We need this to quickly fetch historical data
        self.monthly_df = self.df.groupby(['Crop', 'State Name', 'District Name', 'Mandi', 'YearMonth']).agg(
            Modal_Price=('Modal Price (Rs./Quintal)', 'median'),
            Arrivals=('Arrivals (Tonnes)', 'sum')
        ).reset_index()
        self.monthly_df['Date'] = self.monthly_df['YearMonth'].dt.to_timestamp()
        
    def _load_supported_mandis(self):
        if not self.models_dir.is_dir():
            return
            
        for path in self.models_dir.glob("*.joblib"):
            if path.name.endswith(".joblib"):
                try:
                    data = joblib.load(path)
                    metadata = data.get('metadata', {})
                    crop = metadata.get('crop')
                    mandi = metadata.get('mandi')
                    
                    if crop and mandi:
                        # Find state and district from data
                        match = self.df[(self.df['Crop'] == crop) & (self.df['Mandi'] == mandi)]
                        if not match.empty:
                            state = match['State Name'].iloc[0]
                            district = match['District Name'].iloc[0]
                            self.supported_pairs.append({
                                'crop': crop,
                                'state': state,
                                'district': district,
                                'mandi': mandi,
                                'strategy': metadata.get('strategy', 'naive')
                            })
                except Exception as e:
                    print(f"Error loading {path.name}: {e}")

    def get_supported_mandis(self):
        return self.supported_pairs

    def is_supported(self, crop: str, mandi: str):
        for pair in self.supported_pairs:
            if pair['crop'] == crop and pair['mandi'] == mandi:
                return pair
        return None

    def get_historical_prices(self, crop: str, mandi: str):
        mask = (self.monthly_df['Crop'] == crop) & (self.monthly_df['Mandi'] == mandi)
        data = self.monthly_df[mask].sort_values('Date')
        return data

    def get_latest_price_info(self, crop: str, mandi: str):
        data = self.get_historical_prices(crop, mandi)
        if data.empty:
            return None, None
        latest_row = data.iloc[-1]
        return latest_row['Date'].strftime('%Y-%m-%d'), latest_row['Modal_Price']
        
    def get_volatility(self, crop: str, mandi: str):
        data = self.get_historical_prices(crop, mandi)
        if len(data) < 2:
            return None
            
        # Get last 12 months
        last_12 = data.tail(13) # need 13 to get 12 pct changes
        pct_change = last_12['Modal_Price'].pct_change().dropna()
        if len(pct_change) == 0:
            return None
        return float(pct_change.std() * 100) # Returns volatility in percentage

# Singleton instance
data_service = DataService()
