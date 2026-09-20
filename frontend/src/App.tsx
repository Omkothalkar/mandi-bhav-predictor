import { useState } from 'react';
import { AnalysisForm } from './components/forms/AnalysisForm';
import type { AnalysisFormData } from './components/forms/AnalysisForm';
import { ComparisonPanel } from './components/results/ComparisonPanel';
import { Methodology } from './components/layout/Methodology';
import { api } from './api/client';
import type { ComparisonResult, CompareRequest } from './types/api.types';
import './App.css';

function App() {
  const [isComparing, setIsComparing] = useState(false);
  const [compareResults, setCompareResults] = useState<ComparisonResult[] | null>(null);
  const [compareError, setCompareError] = useState<string | null>(null);

  const handleAnalyze = async (data: AnalysisFormData) => {
    setIsComparing(true);
    setCompareError(null);
    setCompareResults(null);

    try {
      const compareRequest: CompareRequest = {
        crop: data.crop,
        quantity: data.quantity,
        quantity_unit: data.quantityUnit,
        transport_rate: data.transportRate,
        mandis: [
          {
            crop: data.crop,
            state: data.state,
            district: data.district,
            mandi: data.mandi,
            distance_km: data.distanceKm,
          }
        ]
      };

      const response = await api.compareMandis(compareRequest);
      setCompareResults(response.results);
    } catch (err: any) {
      console.error("Comparison failed:", err);
      if (err.response?.data?.detail) {
        setCompareError(err.response.data.detail);
      } else {
        setCompareError("Failed to fetch market analysis. Please ensure the backend is running and the mandi is supported.");
      }
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: 'var(--spacing-5)' }}>
      <header style={{ marginBottom: 'var(--spacing-8)', textAlign: 'center' }}>
        <h1 style={{ color: 'var(--color-accent-primary)', fontSize: '2.5rem', marginBottom: 'var(--spacing-2)' }}>AgriMandi</h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)' }}>Agricultural Market Price Forecasting & Decision Support</p>
      </header>

      <main>
        <AnalysisForm onSubmit={handleAnalyze} isLoading={isComparing} />
        
        <ComparisonPanel 
          results={compareResults || []} 
          isLoading={isComparing} 
          error={compareError} 
        />

        <Methodology />
      </main>
    </div>
  );
}

export default App;
