export interface DisclaimerMetadata {
    historical_data_start_date: string;
    historical_data_end_date: string;
    limitation: string;
}

export interface SupportedMandi {
    crop: string;
    state: string;
    district: string;
    mandi: string;
}

export interface AvailableMandisResponse {
    supported_mandis: SupportedMandi[];
}

export interface HistoricalPrice {
    date: string;
    price: number;
    arrivals: number | null;
}

export interface HistoricalPricesResponse {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    historical_prices: HistoricalPrice[];
    metadata: DisclaimerMetadata;
}

export interface ForecastRequest {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    horizon: number;
}

export interface ForecastedPrice {
    date: string;
    price: number;
}

export interface ForecastResponse {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    forecast_horizon: number;
    latest_known_historical_date: string;
    latest_known_price: number;
    forecasted_prices: ForecastedPrice[];
    forecast_strategy: string;
    metadata: DisclaimerMetadata;
}

export interface CompareMandiRequest {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    distance_km: number;
}

export interface CompareRequest {
    crop: string;
    quantity: number;
    quantity_unit: string;
    transport_rate: number;
    mandis: CompareMandiRequest[];
}

export interface ComparisonResult {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    latest_known_historical_price: number;
    forecast_price: number;
    expected_percentage_change: number;
    historical_volatility: number | null;
    transport_cost: number;
    expected_net_return: number;
    decision: string;
    decision_reason: string;
    forecast_strategy: string;
}

export interface CompareResponse {
    results: ComparisonResult[];
    metadata: DisclaimerMetadata;
}
