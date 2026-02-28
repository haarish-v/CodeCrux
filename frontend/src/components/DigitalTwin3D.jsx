import React from 'react';

export const DigitalTwin3D = ({ riskScore = 0.15 }) => {
    // Calculate risk modifiers
    const isCritical = riskScore > 0.8;
    const isWarning = riskScore > 0.5 && riskScore <= 0.8;

    const heartColor = isCritical ? '#ff2a2a' : isWarning ? '#ffcc00' : '#00e5ff';
    const statusText = isCritical ? 'CRITICAL ISCHEMIA / TACHYCARDIA' : isWarning ? 'COMPENSATING' : 'NORMAL PERFUSION';

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>

            <div style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 1
            }}>
                <img
                    src="/realistic_heart.png"
                    alt="Anatomical Heart Twin"
                    className={`heart-sprite ${isCritical ? 'heart-critical' : 'heart-normal'}`}
                    style={{
                        maxWidth: '220px',
                        maxHeight: '220px',
                        // Optional fallback if the extraction script failed to write the alpha channel perfectly:
                        // mixBlendMode: 'screen' 
                    }}
                />
            </div>

            <div style={{
                position: 'absolute',
                bottom: '15px',
                color: heartColor,
                fontSize: '0.75rem',
                fontWeight: 'bold',
                textTransform: 'uppercase',
                zIndex: 2,
                textShadow: `0 0 10px ${heartColor}`
            }}>
                {statusText}
            </div>
        </div>
    );
};
