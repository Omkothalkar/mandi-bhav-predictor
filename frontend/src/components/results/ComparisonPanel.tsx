import React from 'react';
import type { ComparisonResult } from '../../types/api.types';
import { TrendingUp, TrendingDown, ArrowRight, Truck, Info, AlertTriangle } from 'lucide-react';

interface ComparisonPanelProps {
    results: ComparisonResult[];
    isLoading: boolean;
    error: string | null;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({ results, isLoading, error }) => {
    if (isLoading) {
        return (
            <div className="card" style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-8)' }}>
                <p>Analyzing market conditions...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ borderLeft: '4px solid var(--color-status-sell)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-status-sell)' }}>
                    <AlertTriangle size={20} />
                    <strong>Analysis Failed</strong>
                </div>
                <p style={{ marginTop: '8px', marginBottom: 0 }}>{error}</p>
            </div>
        );
    }

    if (!results || results.length === 0) {
        return null;
    }

    // Since we only pass the selected mandi, we just take the first result
    const result = results[0];

    const isWait = result.decision.toUpperCase() === 'WAIT';
    const decisionColor = isWait ? 'var(--color-status-wait)' : 'var(--color-status-sell)';

    return (
        <div className="card" style={{ marginTop: 'var(--spacing-5)' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--spacing-5)' }}>Selected Mandi Analysis</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-4)', marginBottom: 'var(--spacing-5)' }}>
                
                {/* Price Information */}
                <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-bg-primary)', borderRadius: 'var(--radius-md)' }}>
                    <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-2)' }}>Price Outlook (₹/Quintal)</h3>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--spacing-3)' }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: 600 }}>₹{result.latest_known_historical_price.toFixed(2)}</span>
                        <ArrowRight size={16} color="var(--color-text-tertiary)" />
                        <span style={{ fontSize: '1.5rem', fontWeight: 600 }}>₹{result.forecast_price.toFixed(2)}</span>
                    </div>
                    <div style={{ marginTop: 'var(--spacing-2)', display: 'flex', alignItems: 'center', gap: '4px', color: result.expected_percentage_change >= 0 ? 'var(--color-status-wait)' : 'var(--color-status-sell)', fontSize: '0.875rem', fontWeight: 500 }}>
                        {result.expected_percentage_change >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                        {Math.abs(result.expected_percentage_change).toFixed(2)}% expected change
                    </div>
                </div>

                {/* Return Information */}
                <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-bg-primary)', borderRadius: 'var(--radius-md)' }}>
                    <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-2)' }}>Expected Net Return</h3>
                    <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>₹{result.expected_net_return.toFixed(2)}</div>
                    <div style={{ marginTop: 'var(--spacing-2)', display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                        <Truck size={16} />
                        Transport cost: ₹{result.transport_cost.toFixed(2)}
                    </div>
                </div>

                {/* Risk & Strategy */}
                <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-bg-primary)', borderRadius: 'var(--radius-md)' }}>
                    <h3 style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-2)' }}>Risk & Strategy</h3>
                    <div style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '4px' }}>
                        Volatility: {result.historical_volatility ? `${result.historical_volatility.toFixed(2)}%` : 'N/A'}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                        <Info size={16} />
                        Strategy: {result.forecast_strategy}
                    </div>
                </div>

            </div>

            {/* Decision Block */}
            <div style={{ 
                borderLeft: `4px solid ${decisionColor}`, 
                backgroundColor: isWait ? 'var(--color-accent-light)' : '#fee2e2',
                padding: 'var(--spacing-4)', 
                borderRadius: '0 var(--radius-md) var(--radius-md) 0'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)', color: decisionColor, marginBottom: 'var(--spacing-1)' }}>
                    <span style={{ fontSize: '1.25rem', fontWeight: 700 }}>{result.decision.toUpperCase()}</span>
                </div>
                <p style={{ margin: 0, color: 'var(--color-text-primary)', fontWeight: 500 }}>{result.decision_reason}</p>
            </div>
            
        </div>
    );
};
