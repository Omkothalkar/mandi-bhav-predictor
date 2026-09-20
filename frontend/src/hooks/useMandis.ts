import { useState, useEffect, useMemo } from 'react';
import { api } from '../api/client';
import type { SupportedMandi } from '../types/api.types';

export function useMandis() {
    const [mandis, setMandis] = useState<SupportedMandi[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Selections
    const [selectedCrop, setSelectedCrop] = useState<string>('');
    const [selectedState, setSelectedState] = useState<string>('');
    const [selectedDistrict, setSelectedDistrict] = useState<string>('');
    const [selectedMandi, setSelectedMandi] = useState<string>('');

    useEffect(() => {
        const fetchMandis = async () => {
            try {
                const data = await api.getAvailableMandis();
                setMandis(data.supported_mandis);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch mandis", err);
                setError("Unable to connect to the AgriMandi API. Please check that the backend is running.");
            } finally {
                setLoading(false);
            }
        };
        fetchMandis();
    }, []);

    const crops = useMemo(() => Array.from(new Set(mandis.map(m => m.crop))).sort(), [mandis]);
    
    const states = useMemo(() => {
        if (!selectedCrop) return [];
        return Array.from(new Set(mandis.filter(m => m.crop === selectedCrop).map(m => m.state))).sort();
    }, [mandis, selectedCrop]);

    const districts = useMemo(() => {
        if (!selectedCrop || !selectedState) return [];
        return Array.from(new Set(
            mandis
                .filter(m => m.crop === selectedCrop && m.state === selectedState)
                .map(m => m.district)
        )).sort();
    }, [mandis, selectedCrop, selectedState]);

    const availableMandis = useMemo(() => {
        if (!selectedCrop || !selectedState || !selectedDistrict) return [];
        return mandis
            .filter(m => m.crop === selectedCrop && m.state === selectedState && m.district === selectedDistrict)
            .map(m => m.mandi)
            .sort();
    }, [mandis, selectedCrop, selectedState, selectedDistrict]);

    // Reset dependents when a parent changes
    const handleCropChange = (crop: string) => {
        setSelectedCrop(crop);
        setSelectedState('');
        setSelectedDistrict('');
        setSelectedMandi('');
    };

    const handleStateChange = (state: string) => {
        setSelectedState(state);
        setSelectedDistrict('');
        setSelectedMandi('');
    };

    const handleDistrictChange = (district: string) => {
        setSelectedDistrict(district);
        setSelectedMandi('');
    };

    const handleMandiChange = (mandi: string) => {
        setSelectedMandi(mandi);
    };

    return {
        loading,
        error,
        mandis,
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
    };
}
