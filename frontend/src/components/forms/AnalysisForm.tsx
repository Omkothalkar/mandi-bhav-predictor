import React, { useState } from 'react';
import { useMandis } from '../../hooks/useMandis';
import { AlertCircle } from 'lucide-react';

export interface AnalysisFormData {
    crop: string;
    state: string;
    district: string;
    mandi: string;
    quantity: number;
    quantityUnit: 'quintals' | 'tonnes';
    distanceKm: number;
    transportRate: number;
    horizon: number;
}

interface AnalysisFormProps {
    onSubmit: (data: AnalysisFormData) => void;
    isLoading: boolean;
}

export const AnalysisForm: React.FC<AnalysisFormProps> = ({ onSubmit, isLoading }) => {
    const {
        loading: mandisLoading,
        error: mandisError,
        crops,
        states,
        districts,
        availableMandis,
        selectedCrop,
        selectedState,
        selectedDistrict,
        selectedMandi,
        handleCropChange,
        handleStateChange,
        handleDistrictChange,
        handleMandiChange
    } = useMandis();

    const [quantity, setQuantity] = useState<number | ''>('');
    const [quantityUnit, setQuantityUnit] = useState<'quintals' | 'tonnes'>('tonnes');
    const [distanceKm, setDistanceKm] = useState<number | ''>('');
    const [transportRate, setTransportRate] = useState<number | ''>('');
    const [horizon, setHorizon] = useState<number>(3);
    const [validationError, setValidationError] = useState<string | null>(null);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setValidationError(null);

        if (!selectedCrop || !selectedState || !selectedDistrict || !selectedMandi) {
            setValidationError("Please select a complete Crop-Mandi combination.");
            return;
        }

        if (quantity === '' || quantity <= 0) {
            setValidationError("Quantity must be greater than 0.");
            return;
        }

        if (distanceKm === '' || distanceKm < 0) {
            setValidationError("Distance cannot be negative.");
            return;
        }

        if (transportRate === '' || transportRate < 0) {
            setValidationError("Transport rate cannot be negative.");
            return;
        }

        if (horizon < 1 || horizon > 24) {
            setValidationError("Forecast horizon must be between 1 and 24 months.");
            return;
        }

        onSubmit({
            crop: selectedCrop,
            state: selectedState,
            district: selectedDistrict,
            mandi: selectedMandi,
            quantity: Number(quantity),
            quantityUnit,
            distanceKm: Number(distanceKm),
            transportRate: Number(transportRate),
            horizon: Number(horizon)
        });
    };

    if (mandisError) {
        return (
            <div className="card" style={{ borderLeft: '4px solid var(--color-status-sell)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-status-sell)' }}>
                    <AlertCircle size={20} />
                    <strong>API Connection Error</strong>
                </div>
                <p style={{ marginTop: '8px', marginBottom: 0 }}>{mandisError}</p>
            </div>
        );
    }

    return (
        <form className="card" onSubmit={handleSubmit}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--spacing-5)' }}>Market Analysis Setup</h2>
            
            {validationError && (
                <div style={{ padding: '12px', backgroundColor: '#fef2f2', color: '#dc2626', borderRadius: '4px', marginBottom: '16px', fontSize: '0.875rem' }}>
                    {validationError}
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <div className="form-group">
                    <label className="form-label">Crop</label>
                    <select 
                        className="form-control" 
                        value={selectedCrop} 
                        onChange={(e) => handleCropChange(e.target.value)}
                        disabled={mandisLoading}
                    >
                        <option value="">Select Crop</option>
                        {crops.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">State</label>
                    <select 
                        className="form-control" 
                        value={selectedState} 
                        onChange={(e) => handleStateChange(e.target.value)}
                        disabled={!selectedCrop || mandisLoading}
                    >
                        <option value="">Select State</option>
                        {states.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">District</label>
                    <select 
                        className="form-control" 
                        value={selectedDistrict} 
                        onChange={(e) => handleDistrictChange(e.target.value)}
                        disabled={!selectedState || mandisLoading}
                    >
                        <option value="">Select District</option>
                        {districts.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                </div>

                <div className="form-group">
                    <label className="form-label">Mandi</label>
                    <select 
                        className="form-control" 
                        value={selectedMandi} 
                        onChange={(e) => handleMandiChange(e.target.value)}
                        disabled={!selectedDistrict || mandisLoading}
                    >
                        <option value="">Select Mandi</option>
                        {availableMandis.map(m => <option key={m} value={m}>{m}</option>)}
                    </select>
                </div>
            </div>

            <div style={{ borderTop: '1px solid var(--color-border-subtle)', margin: '16px 0' }}></div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                <div className="form-group">
                    <label className="form-label">Quantity</label>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <input 
                            type="number" 
                            className="form-control" 
                            min="0.1" 
                            step="0.1"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value ? Number(e.target.value) : '')}
                            placeholder="e.g. 10"
                        />
                        <select 
                            className="form-control" 
                            style={{ width: '120px' }}
                            value={quantityUnit}
                            onChange={(e) => setQuantityUnit(e.target.value as 'quintals' | 'tonnes')}
                        >
                            <option value="tonnes">Tonnes</option>
                            <option value="quintals">Quintals</option>
                        </select>
                    </div>
                </div>

                <div className="form-group">
                    <label className="form-label">Distance (km)</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        min="0"
                        value={distanceKm}
                        onChange={(e) => setDistanceKm(e.target.value ? Number(e.target.value) : '')}
                        placeholder="e.g. 150"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Transport Rate (₹/km/Quintal)</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        min="0" 
                        step="0.1"
                        value={transportRate}
                        onChange={(e) => setTransportRate(e.target.value ? Number(e.target.value) : '')}
                        placeholder="e.g. 2.5"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Forecast Horizon (Months)</label>
                    <select 
                        className="form-control"
                        value={horizon}
                        onChange={(e) => setHorizon(Number(e.target.value))}
                    >
                        {[1, 2, 3, 6, 12].map(m => (
                            <option key={m} value={m}>{m} Month{m > 1 ? 's' : ''}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                <button type="submit" className="btn btn-primary" disabled={isLoading || mandisLoading}>
                    {isLoading ? 'Analyzing...' : 'Analyze Market'}
                </button>
            </div>
        </form>
    );
};
