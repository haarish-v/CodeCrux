import React from 'react';

export const AlertLog = ({ riskScore, scenario, isMuted, setIsMuted, clinicalNote, isGeneratingNote, onGenerateNote }) => {
    const isCritical = riskScore > 0.8;
    const isWarning = riskScore > 0.5 && riskScore <= 0.8;

    const playTTS = () => {
        if (!clinicalNote) return;
        window.speechSynthesis.cancel(); // Stop any currently playing audio
        const utterance = new SpeechSynthesisUtterance(clinicalNote);

        // Find a professional-sounding female/male English voice if available
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha') || v.lang === 'en-US');
        if (preferredVoice) utterance.voice = preferredVoice;

        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

            {/* Risk Score Indicator */}
            <div style={{ paddingBottom: '15px', borderBottom: '1px solid var(--panel-border)', marginBottom: '15px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '5px' }}>FUSION RISK SCORE</div>
                <div style={{
                    fontSize: '2rem',
                    fontWeight: 'bold',
                    color: isCritical ? 'var(--text-alert)' : isWarning ? 'var(--text-warning)' : 'var(--text-success)',
                    textShadow: isCritical ? '0 0 10px rgba(255,0,0,0.5)' : 'none'
                }}>
                    {(riskScore * 100).toFixed(1)}%
                </div>
            </div>

            {/* Log Entries */}
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>

                {isCritical && (
                    <div style={{ padding: '10px', background: 'rgba(255, 42, 42, 0.1)', borderLeft: '3px solid var(--text-alert)' }}>
                        <div style={{ color: 'var(--text-alert)', fontWeight: 'bold', fontSize: '0.8rem' }}>CRITICAL ALERT</div>
                        <div style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                            High probability of Code Blue in next 6hrs.<br />
                            <span style={{ color: 'var(--text-muted)' }}>→ Source: FusionNet (ECG + Vitals)</span>
                        </div>
                        {!isMuted ? (
                            <button
                                onClick={() => setIsMuted(true)}
                                style={{
                                    marginTop: '15px',
                                    width: '100%',
                                    padding: '8px',
                                    background: 'transparent',
                                    color: 'var(--text-alert)',
                                    border: '1px solid var(--text-alert)',
                                    cursor: 'pointer',
                                    fontSize: '0.7rem',
                                    fontFamily: 'monospace',
                                    textTransform: 'uppercase',
                                    transition: 'all 0.3s'
                                }}
                                onMouseOver={(e) => { e.target.style.background = 'rgba(255,42,42,0.1)'; }}
                                onMouseOut={(e) => { e.target.style.background = 'transparent'; }}
                            >
                                🔇 ACKNOWLEDGE ALARM
                            </button>
                        ) : (
                            <div style={{ marginTop: '15px', fontSize: '0.7rem', color: 'var(--text-warning)', fontStyle: 'italic', textAlign: 'center' }}>
                                🔇 ALARM ACKNOWLEDGED
                            </div>
                        )}
                    </div>
                )}

                {scenario === 'rapid_descent' && (
                    <div style={{ padding: '10px', background: 'rgba(255, 204, 0, 0.1)', borderLeft: '3px solid var(--text-warning)' }}>
                        <div style={{ color: 'var(--text-warning)', fontWeight: 'bold', fontSize: '0.8rem' }}>WARNING</div>
                        <div style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                            Rapid SpO2 desaturation detected.<br />
                            <span style={{ color: 'var(--text-muted)' }}>→ Source: VitalsGRU</span>
                        </div>
                    </div>
                )}

                {!isCritical && scenario === 'stable' && (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.8rem', padding: '20px' }}>
                        NO ACTIVE ALERTS<br /><br />
                        Aegis-Omni Multi-Modal Synthesis confirms patient stability.
                    </div>
                )}

                {/* AI Doctor Note Section */}
                <div style={{ marginTop: 'auto', paddingTop: '15px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-main)', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>A.I. CLINICAL SYNTHESIS</span>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {clinicalNote && (
                                <button
                                    onClick={playTTS}
                                    style={{
                                        background: 'transparent',
                                        border: '1px solid rgba(0, 229, 255, 0.5)',
                                        color: 'var(--text-main)',
                                        padding: '4px 8px',
                                        fontSize: '0.65rem',
                                        cursor: 'pointer',
                                        fontFamily: 'var(--font-mono)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '4px'
                                    }}
                                    title="Read Aloud"
                                >
                                    🔊 READ
                                </button>
                            )}
                            <button
                                onClick={onGenerateNote}
                                disabled={isGeneratingNote}
                                style={{
                                    background: 'transparent',
                                    border: '1px solid var(--text-main)',
                                    color: isGeneratingNote ? 'var(--text-muted)' : 'var(--text-main)',
                                    borderColor: isGeneratingNote ? 'var(--text-muted)' : 'var(--text-main)',
                                    padding: '4px 8px',
                                    fontSize: '0.65rem',
                                    cursor: isGeneratingNote ? 'not-allowed' : 'pointer',
                                    fontFamily: 'var(--font-mono)'
                                }}
                            >
                                {isGeneratingNote ? 'SYNTHESIZING...' : 'GENERATE NOTE'}
                            </button>
                        </div>
                    </div>
                    {clinicalNote && (
                        <div style={{
                            padding: '10px',
                            background: 'rgba(0, 229, 255, 0.05)',
                            borderLeft: '2px solid var(--text-main)',
                            fontSize: '0.7rem',
                            color: 'var(--text-main)',
                            lineHeight: '1.4',
                            whiteSpace: 'pre-wrap'
                        }}>
                            {clinicalNote}
                        </div>
                    )}
                </div>
            </div>

        </div>
    );
};
