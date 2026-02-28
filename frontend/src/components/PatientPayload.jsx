import React, { useState, useEffect } from 'react';

export const PatientPayload = () => {
    const [glitchText, setGlitchText] = useState('');

    // Simulate an encrypted flowing stream
    useEffect(() => {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
        const interval = setInterval(() => {
            let text = '';
            for (let i = 0; i < 64; i++) {
                text += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            setGlitchText(text);
        }, 500); // Glitch every 500ms

        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', fontSize: '0.8rem' }}>
            <div style={{
                flex: 1,
                color: 'var(--text-muted)',
                wordBreak: 'break-all',
                fontFamily: 'var(--font-mono)',
                overflow: 'hidden',
                marginBottom: '10px'
            }}>
                {glitchText}
            </div>

            <div style={{ borderTop: '1px solid var(--panel-border)', paddingTop: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>PATIENT ID:</span>
                    <span>PT-7423</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>DEVICE:</span>
                    <span>AG-ALPHA-081</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>WARD:</span>
                    <span>ICU - BED 4</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>TIMESTAMP:</span>
                    <span>{new Date().toISOString().split('T')[1].split('.')[0]} UTC</span>
                </div>
            </div>
        </div>
    );
};
