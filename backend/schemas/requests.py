from pydantic import BaseModel, Field
from typing import List, Optional

class ForecastRequest(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str
    horizon: int = Field(..., gt=0, le=24, description="Forecast horizon in months (1-24)")

class CompareMandiRequest(BaseModel):
    crop: str
    state: str
    district: str
    mandi: str
    distance_km: float = Field(..., ge=0, description="User-provided distance in km")

class CompareRequest(BaseModel):
    crop: str
    quantity: float = Field(..., gt=0, description="Quantity")
    quantity_unit: str = Field(..., pattern="^(quintals|tonnes)$", description="Unit of quantity (quintals or tonnes)")
    transport_rate: float = Field(..., ge=0, description="Transport rate in Rs per km per quintal")
    mandis: List[CompareMandiRequest] = Field(..., min_items=1)
