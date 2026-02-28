import React from 'react';

const TelemetryItem = ({ label, value, unit, status }) => {
    // Determine color based on status if provided (normal, warning, critical)
    let colorClass = 'text-main';
    if (status === 'critical') colorClass = 'status-critical';
    else if (status === 'warning') colorClass = 'text-warning';

    return (
        <div style={{ padding: '8px', borderBottom: '1px solid var(--panel-border)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{label}</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }} className={colorClass}>
                    {value}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{unit}</div>
            </div>
        </div>
    );
};

export const TelemetryPanel = ({ vitals }) => {
    // Mock logic to determine if a vital is out of bounds
    const getStatus = (label, value) => {
        if (!value || value === '--') return 'normal';
        if (label === 'HR') return value > 120 || value < 50 ? 'critical' : value > 100 ? 'warning' : 'normal';
        if (label === 'SpO2') return value < 90 ? 'critical' : value < 94 ? 'warning' : 'normal';
        if (label === 'MAP') return value < 65 ? 'critical' : 'normal';
        if (label === 'RESP') return value > 30 || value < 8 ? 'critical' : value > 25 ? 'warning' : 'normal';
        return 'normal';
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <TelemetryItem label="HR" value={vitals?.HR || '--'} unit="bpm" status={getStatus('HR', vitals?.HR)} />
            <TelemetryItem label="SpO2" value={vitals?.SpO2 || '--'} unit="%" status={getStatus('SpO2', vitals?.SpO2)} />
            <TelemetryItem label="MAP" value={vitals?.MAP || '--'} unit="mmHg" status={getStatus('MAP', vitals?.MAP)} />
            <TelemetryItem label="RESP" value={vitals?.RESP || '--'} unit="rpm" status={getStatus('RESP', vitals?.RESP)} />
        </div>
    );
};
