import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const Methodology: React.FC = () => {
    return (
        <div className="card" style={{ marginTop: 'var(--spacing-5)' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: 'var(--spacing-5)' }}>Methodology & Limitations</h2>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Dataset</h3>
                <p>
                    This system uses Agmarknet historical mandi data. The current project subset covers the period from <strong>2012 to 2017</strong>.
                    Wheat and Rice were used for the current modeling workflow.
                </p>
                <p>
                    The data contains mandi-level information such as State, District, Market, Variety, Arrivals, Min Price, Max Price, Modal Price, and Reported Date.
                </p>
            </div>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Data Processing</h3>
                <p>
                    The project performs comprehensive data cleaning including date conversion, numeric validation, invalid price filtering, duplicate aggregation, and exploratory data analysis.
                </p>
            </div>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Forecasting</h3>
                <p>
                    The current selected forecasting strategy is: <strong>Naive — Previous Month Price</strong>.
                </p>
                <p>
                    The naive strategy uses the latest known price as the next forecast and recursively carries the forecast forward for additional months. 
                    This can result in a flat multi-month forecast. That is expected behavior and must NOT be artificially changed.
                </p>
            </div>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Model Evaluation</h3>
                <p>
                    Models were evaluated using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE).
                </p>
                <p>
                    The naive previous-month strategy had the lowest measured test error among the tested strategies for the selected crop–mandi series.
                </p>
            </div>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Decision Engine</h3>
                <p>
                    The backend combines historical/latest price, forecast price, quantity, transport cost, expected gross revenue, expected net return, and volatility to produce a rule-based <strong>SELL / WAIT</strong> decision.
                </p>
            </div>

            <div style={{ marginBottom: 'var(--spacing-5)' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)' }}>Transport Cost</h3>
                <p>Transport Cost = Distance × Transport Rate × Quantity in Quintals</p>
                <p><em>Note: 1 tonne = 10 quintals</em></p>
            </div>

            <div style={{ backgroundColor: '#fef3c7', padding: 'var(--spacing-4)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #f59e0b' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--spacing-3)', display: 'flex', alignItems: 'center', gap: '8px', color: '#b45309' }}>
                    <AlertTriangle size={20} />
                    Limitations
                </h3>
                <ul style={{ listStyleType: 'disc', paddingLeft: 'var(--spacing-5)', color: '#92400e' }}>
                    <li><strong>Historical Agmarknet data available through June 2017. Forecasts are generated from historical data and do not represent live market prices.</strong></li>
                    <li>Forecast support currently exists only for the modeled crop–mandi series.</li>
                    <li>Distance and transport rate are user-provided.</li>
                    <li>The naive recursive forecast can remain flat across multiple forecast months.</li>
                    <li>The system is a decision-support prototype and does not guarantee future prices or profit.</li>
                </ul>
            </div>
        </div>
    );
};
