from fastapi import APIRouter, HTTPException
from typing import List, Optional

from backend.schemas.requests import ForecastRequest, CompareRequest
from backend.schemas.responses import (
    AvailableMandisResponse, HistoricalPricesResponse, 
    ForecastResponse, CompareResponse, SupportedMandi,
    HistoricalPrice, DisclaimerMetadata, ForecastedPrice, ComparisonResult
)
from backend.services.data_service import data_service
from backend.services.forecasting import forecasting_service
from backend.services.decision_engine import decision_engine

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/available-mandis", response_model=AvailableMandisResponse)
def get_available_mandis():
    supported = data_service.get_supported_mandis()
    mandis = [SupportedMandi(**s) for s in supported]
    return AvailableMandisResponse(supported_mandis=mandis)

@router.get("/historical-prices", response_model=HistoricalPricesResponse)
def get_historical_prices(crop: str, mandi: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    data = data_service.get_historical_prices(crop, mandi)
    if data.empty:
        raise HTTPException(status_code=404, detail="Historical data not found for the requested crop and mandi.")
        
    # Optional date filtering
    if start_date:
        data = data[data['Date'] >= start_date]
    if end_date:
        data = data[data['Date'] <= end_date]
        
    prices = []
    for _, row in data.iterrows():
        prices.append(HistoricalPrice(
            date=row['Date'].strftime('%Y-%m-%d'),
            price=row['Modal_Price'],
            arrivals=row['Arrivals']
        ))
        
    return HistoricalPricesResponse(
        crop=crop, state=data.iloc[0]['State Name'], district=data.iloc[0]['District Name'], mandi=mandi,
        historical_prices=prices
    )

@router.post("/forecast", response_model=ForecastResponse)
def generate_forecast(req: ForecastRequest):
    support_info = data_service.is_supported(req.crop, req.mandi)
    if not support_info:
        raise HTTPException(status_code=404, detail="Forecasting is not supported for this Crop-Mandi pair.")
        
    latest_date, latest_price = data_service.get_latest_price_info(req.crop, req.mandi)
    if latest_date is None:
        raise HTTPException(status_code=404, detail="No historical data available to generate forecast.")
        
    strategy = support_info['strategy']
    
    forecasts = forecasting_service.generate_forecast(
        latest_date, latest_price, req.horizon, strategy, req.crop, req.mandi
    )
    
    forecast_prices = [ForecastedPrice(date=f['date'], price=f['price']) for f in forecasts]
    
    return ForecastResponse(
        crop=req.crop,
        state=req.state,
        district=req.district,
        mandi=req.mandi,
        forecast_horizon=req.horizon,
        latest_known_historical_date=latest_date,
        latest_known_price=latest_price,
        forecasted_prices=forecast_prices,
        forecast_strategy=strategy
    )

@router.post("/compare", response_model=CompareResponse)
def compare_mandis(req: CompareRequest):
    results = []
    
    for mandi_req in req.mandis:
        support_info = data_service.is_supported(req.crop, mandi_req.mandi)
        if not support_info:
            raise HTTPException(status_code=404, detail=f"Forecasting not supported for {req.crop} in {mandi_req.mandi}")
            
        latest_date, latest_price = data_service.get_latest_price_info(req.crop, mandi_req.mandi)
        if latest_price is None:
            raise HTTPException(status_code=404, detail=f"No data for {mandi_req.mandi}")
            
        strategy = support_info['strategy']
        
        # 1-month forecast
        forecasts = forecasting_service.generate_forecast(latest_date, latest_price, 1, strategy, req.crop, mandi_req.mandi)
        forecast_price = forecasts[0]['price']
        
        pct_change = ((forecast_price - latest_price) / latest_price) * 100 if latest_price > 0 else 0
        
        volatility = data_service.get_volatility(req.crop, mandi_req.mandi)
        
        # Current costs
        current_transport = decision_engine.calculate_transport_cost(
            mandi_req.distance_km, req.transport_rate, req.quantity, req.quantity_unit
        )
        current_gross, current_net = decision_engine.calculate_net_return(
            latest_price, req.quantity, req.quantity_unit, current_transport
        )
        
        # Forecast costs
        forecast_gross, forecast_net = decision_engine.calculate_net_return(
            forecast_price, req.quantity, req.quantity_unit, current_transport
        )
        
        # Decision
        decision, reason = decision_engine.generate_decision(current_net, forecast_net)
        
        results.append(ComparisonResult(
            crop=req.crop,
            state=mandi_req.state,
            district=mandi_req.district,
            mandi=mandi_req.mandi,
            latest_known_historical_price=latest_price,
            forecast_price=forecast_price,
            expected_percentage_change=round(pct_change, 2),
            historical_volatility=round(volatility, 2) if volatility else None,
            transport_cost=current_transport,
            expected_net_return=forecast_net,
            decision=decision,
            decision_reason=reason,
            forecast_strategy=strategy
        ))
        
    return CompareResponse(results=results)
