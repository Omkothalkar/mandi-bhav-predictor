from pydantic import BaseModel, Field
from typing import List, Optional

class DisclaimerMetadata(BaseModel):
    historical_data_start_date: str = "2012-01-01"
    historical_data_end_date: str = "2017-06-30"
    limitation: str = "Forecasts are generated recursively from historical data ending in June 2017. They do not represent live 2026 market predictions."

class SupportedMandi(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str

class AvailableMandisResponse(BaseModel):
    supported_mandis: List[SupportedMandi]

class HistoricalPrice(BaseModel):
    date: str
    price: float
    arrivals: Optional[float] = None

class HistoricalPricesResponse(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str
    historical_prices: List[HistoricalPrice]
    metadata: DisclaimerMetadata = Field(default_factory=DisclaimerMetadata)

class ForecastedPrice(BaseModel):
    date: str
    price: float

class ForecastResponse(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str
    forecast_horizon: int
    latest_known_historical_date: str
    latest_known_price: float
    forecasted_prices: List[ForecastedPrice]
    forecast_strategy: str
    metadata: DisclaimerMetadata = Field(default_factory=DisclaimerMetadata)

class ComparisonResult(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str
    latest_known_historical_price: float
    forecast_price: float
    expected_percentage_change: float
    historical_volatility: Optional[float]
    transport_cost: float
    expected_net_return: float
    decision: str
    decision_reason: str
    forecast_strategy: str

class CompareResponse(BaseModel):
    results: List[ComparisonResult]
    metadata: DisclaimerMetadata = Field(default_factory=DisclaimerMetadata)
