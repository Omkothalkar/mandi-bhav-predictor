import axios from 'axios';
import type {
    AvailableMandisResponse,
    HistoricalPricesResponse,
    ForecastRequest,
    ForecastResponse,
    CompareRequest,
    CompareResponse
} from '../types/api.types';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    checkHealth: async () => {
        const response = await apiClient.get('/health');
        return response.data;
    },
    
    getAvailableMandis: async (): Promise<AvailableMandisResponse> => {
        const response = await apiClient.get('/available-mandis');
        return response.data;
    },
    
    getHistoricalPrices: async (crop: string, mandi: string): Promise<HistoricalPricesResponse> => {
        // Make sure to encode the mandi name as it contains spaces and hyphens
        const response = await apiClient.get(`/historical-prices?crop=${encodeURIComponent(crop)}&mandi=${encodeURIComponent(mandi)}`);
        return response.data;
    },
    
    generateForecast: async (request: ForecastRequest): Promise<ForecastResponse> => {
        const response = await apiClient.post('/forecast', request);
        return response.data;
    },
    
    compareMandis: async (request: CompareRequest): Promise<CompareResponse> => {
        const response = await apiClient.post('/compare', request);
        return response.data;
    }
};
