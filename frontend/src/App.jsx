import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import { TelemetryPanel } from './components/TelemetryPanel';
import { PatientPayload } from './components/PatientPayload';
import { AlertLog } from './components/AlertLog';
import { ECGWaveform } from './components/ECGWaveform';
import { DigitalTwin3D } from './components/DigitalTwin3D';
import { Login } from './components/Login';

function App() {
    const [telemetry, setTelemetry] = useState(null);
    const [connected, setConnected] = useState(false);
    const [scenario, setScenario] = useState('stable');
    const [uptime, setUptime] = useState(0);
    const [uploadResults, setUploadResults] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    // Auth State
    const [authData, setAuthData] = useState(null);
    const [authError, setAuthError] = useState(null);

    // MySQL Database Bindings
    const [patientInfo, setPatientInfo] = useState(null);
    const [isMuted, setIsMuted] = useState(false);
    const [clinicalNote, setClinicalNote] = useState(null);
    const [isGeneratingNote, setIsGeneratingNote] = useState(false);
    const fileInputRef = useRef(null);

    // Manage ECG scrolling window
    const ecgBuffer = useRef(Array(300).fill(-1.5));
    const [chartData, setChartData] = useState([]);

    useEffect(() => {
        // Simple Uptime counter
        const timer = setInterval(() => setUptime(u => u + 1), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        // Attempt WebSocket connection to FastAPI backend
        let ws;
        const connectWs = () => {
            ws = new WebSocket(`ws://${window.location.hostname}:8000/telemetry`);

            ws.onopen = () => setConnected(true);
            ws.onclose = () => {
                setConnected(false);
                setTimeout(connectWs, 3000); // Reconnect loop
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setTelemetry(data);

                // Update ECG rolling buffer
                if (data.ecg_wave && data.ecg_wave.length > 0) {
                    // Very rudimentary downsampling if the chunk is huge
                    // Or just append and shift
                    const newValues = data.ecg_wave;
                    const buffer = ecgBuffer.current;

                    // Shift out old, push in new
                    for (let i = 0; i < newValues.length; i++) {
                        // Read every 5th point to condense viewing window, MITDB is 360Hz
                        if (i % 5 === 0) {
                            buffer.shift();
                            buffer.push(newValues[i]);
                        }
                    }
                    // Trigger re-render of chart
                    setChartData([...buffer]);
                }
            };
        };

        connectWs();
        return () => {
            if (ws) ws.close();
        };
    }, []);

    const handleGenerateNote = async () => {
        if (!patientInfo || !telemetry) return;
        setIsGeneratingNote(true);
        setClinicalNote(null);
        try {
            const riskValue = telemetry?.ai_insight?.fusion_risk_score || 0.15;
            const payload = {
                patient_id: patientInfo.patient_id.toString(),
                name: patientInfo.name,
                age: patientInfo.age,
                sex: patientInfo.sex,
                device: patientInfo.device,
                ward: patientInfo.ward,
                risk_score: riskValue,
                is_critical: riskValue > 0.8,
                medications: patientInfo.medications || [],
                vitals_snapshot: telemetry.vitals || {}
            };
            const host = window.location.hostname || 'localhost';
            const response = await fetch(`http://${host}:8000/api/generate_clinical_note/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                const data = await response.json();
                setClinicalNote(data.note);
            } else {
                setClinicalNote("Error: Could not synthesize clinical note.");
            }
        } catch (e) {
            console.error(e);
            setClinicalNote("Error: Connection failed.");
        } finally {
            setIsGeneratingNote(false);
        }
    };

    const handleInject = async (type) => {
        setScenario(type);
        setIsMuted(false); // Reset mute state when patient/scenario changes
        setClinicalNote(null); // Clear previous AI note
        setAuthError(null);    // Clear any previous auth errors

        try {
            await fetch(`http://${window.location.hostname}:8000/api/scenario/${type}`, { method: 'POST' });

            // Fetch synchronized MySQL DB Details for this patient ID
            const riskId = isNaN(type) ? (type === 'critical' ? '231' : '100') : type;

            const headers = {};
            if (authData && authData.access_token) {
                headers['Authorization'] = `Bearer ${authData.access_token}`;
            }

            const res = await fetch(`http://${window.location.hostname}:8000/api/patient/${riskId}`, {
                headers: headers
            });

            if (res.ok) {
                const dbInfo = await res.json();
                setPatientInfo(dbInfo);
            } else if (res.status === 401 || res.status === 403) {
                const errData = await res.json();
                setAuthError(`[ACCESS DENIED] ${errData.detail}`);
                setPatientInfo(null); // Clear patient info on denial
            } else {
                setPatientInfo(null);
            }
        } catch (e) {
            console.error("Failed to inject scenario or fetch DB", e);
        }
    };

    // Initial Load - wait for auth before loading
    useEffect(() => {
        if (authData) {
            handleInject('100');
        }
    }, [authData]);

    const riskScore = telemetry?.ai_insight?.fusion_risk_score || 0.15;
    const isCritical = riskScore > 0.8;

    // Critical Audio Alarm Synthesizer
    useEffect(() => {
        if (!isCritical || isMuted) return;

        let isActive = true;
        let audioCtx;
        let alarmInterval;

        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();

            const playBeep = () => {
                if (!isActive || !audioCtx) return;
                if (audioCtx.state === 'closed') return;
                if (audioCtx.state === 'suspended') audioCtx.resume();

                try {
                    const oscillator = audioCtx.createOscillator();
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);

                    const gainNode = audioCtx.createGain();
                    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
                    gainNode.gain.linearRampToValueAtTime(0.15, audioCtx.currentTime + 0.02);
                    gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.15);

                    oscillator.connect(gainNode);
                    gainNode.connect(audioCtx.destination);

                    oscillator.start();
                    oscillator.stop(audioCtx.currentTime + 0.2);
                } catch (err) {
                    console.log("Audio creation error:", err);
                }
            };

            // Play classic ICU double-beep every 1 second
            alarmInterval = setInterval(() => {
                if (!isActive) return;
                playBeep();
                setTimeout(() => {
                    if (!isActive) return;
                    playBeep();
                }, 200);
            }, 1000);

        } catch (e) {
            console.log("AudioContext blocked or unsupported:", e);
        }

        return () => {
            isActive = false; // Immediately kill any pending timeouts in this closure
            if (alarmInterval) clearInterval(alarmInterval);
            if (audioCtx && audioCtx.state !== 'closed') {
                audioCtx.suspend(); // Force hardware to sleep synchronously
                audioCtx.close().catch(e => console.log("Audio closure delay:", e));
            }
        };
    }, [isCritical, isMuted]);

    // Format uptime
    const formatUptime = (sec) => {
        const h = Math.floor(sec / 3600).toString().padStart(2, '0');
        const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    };

    const handleFileUploadRequest = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (e) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setIsUploading(true);
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('http://localhost:8000/api/upload_predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.results && data.results.length > 0) {
                setUploadResults(data.results);

                // Automatically switch the LIVE background stream to match the uploaded file
                const filename = data.results[0].filename.toLowerCase();
                const recordId = filename.replace('.dat', '').replace('.csv', '').replace('.txt', '');

                // If the user uploads a numeric file, swap the live feed to that patient ID
                if (!isNaN(recordId)) {
                    handleInject(recordId);
                } else if (filename.includes('critical') || filename.includes('200') || filename.includes('231')) {
                    handleInject('231');
                } else {
                    handleInject('stable');
                }
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Upload failed. Ensure backend is running.");
        } finally {
            setIsUploading(false);
            e.target.value = null; // reset
        }
    };

    const handleLogout = () => {
        setAuthData(null);
        setPatientInfo(null);
        setScenario('stable');
    };

    if (!authData) {
        return <Login onLogin={setAuthData} />;
    }

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '10px', gap: '10px' }}>

            {/* HEADER */}
            <header className={`cyber-panel ${isCritical ? 'status-critical-bg' : ''}`} style={{ height: '70px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 20px', transition: 'background 0.5s' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    <div style={{ width: '40px', height: '40px', border: '1px solid var(--text-main)', borderRadius: '4px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={isCritical ? '#ff2a2a' : 'var(--text-main)'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                            <path d="M12 8v4"></path>
                            <path d="M12 16h.01"></path>
                        </svg>
                    </div>
                    <div>
                        <h1 style={{ fontSize: '1.6rem', letterSpacing: '4px', margin: 0, color: isCritical ? '#ff2a2a' : 'inherit' }}>ATRIVA</h1>
                        <div style={{ fontSize: '0.65rem', color: isCritical ? 'rgba(255,42,42,0.8)' : 'var(--text-muted)', letterSpacing: '2px', textTransform: 'uppercase' }}>ADVANCED PREDICTIVE HEALTH TELEMETRY</div>
                    </div>
                </div>

                <div className="header-controls" style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>STREAM SOURCE:</span>
                        <select
                            className="cyber-panel"
                            style={{ padding: '4px 10px', background: 'var(--bg-panel)', color: 'var(--text-main)', borderColor: 'var(--text-main)', cursor: 'pointer', outline: 'none', fontSize: '0.8rem' }}
                            onChange={(e) => handleInject(e.target.value)}
                            value={scenario}
                        >
                            <option value="100">PT-100 (NORMAL)</option>
                            <option value="105">PT-105 (NOISY)</option>
                            <option value="200">PT-200 (ARRHYTHMIA)</option>
                            <option value="231">PT-231 (CRITICAL)</option>
                        </select>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>187</div>
                        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>PACKETS SENT</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>333</div>
                        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>TOTAL ALERTS</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>{formatUptime(uptime)}</div>
                        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>UPTIME</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>AES-256</div>
                        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>ENCRYPTION</div>
                    </div>
                    <div style={{ textAlign: 'center', borderLeft: '1px solid var(--border-glow)', paddingLeft: '15px' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-main)', textTransform: 'uppercase' }}>{authData.user.username}</div>
                        <div style={{ fontSize: '0.55rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{authData.user.role.replace('_', ' ')}</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="cyber-panel"
                        style={{ padding: '6px 15px', color: 'var(--text-main)', borderColor: 'var(--border-glow)', cursor: 'pointer', background: 'transparent', fontSize: '0.7rem' }}
                    >
                        LOGOUT
                    </button>
                    <div className="cyber-panel" style={{ padding: '6px 20px', color: connected ? 'var(--text-success)' : 'var(--text-muted)', borderColor: connected ? 'var(--text-success)' : 'var(--text-muted)', cursor: 'pointer' }} onClick={handleFileUploadRequest} title="Batch Offline Inference">
                        <span className={connected ? "status-live" : ""}>● {connected ? 'LIVE' : 'OFFLINE'}</span>
                    </div>
                    <input type="file" multiple ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} accept=".csv,.dat,.txt" />
                </div>
            </header>

            {/* MAIN CONTENT GRID */}
            <div className="dashboard-grid" style={{ flex: 1, display: 'grid', gridTemplateColumns: '300px 1fr 320px', gap: '10px', height: 'calc(100% - 90px)', gridTemplateAreas: '"left center right"' }}>

                {/* LEFT SIDEBAR - VITALS & PATIENT */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', gridArea: 'left' }}>
                    <div className="cyber-panel" style={{ flex: '1 1 auto', padding: '15px' }}>
                        <div className="panel-title">LIVE TELEMETRY</div>
                        <TelemetryPanel vitals={telemetry?.vitals} />

                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px', fontSize: '0.7rem' }}>
                            <div style={{ border: '1px solid var(--text-success)', color: 'var(--text-success)', padding: '4px 8px' }}>ECG OK</div>
                            <div style={{ border: '1px solid var(--text-success)', color: 'var(--text-success)', padding: '4px 8px' }}>AI ACTIVE</div>
                            <div style={{ border: '1px solid var(--text-success)', color: 'var(--text-success)', padding: '4px 8px' }}>SENSORS</div>
                        </div>
                    </div>

                    <div className="cyber-panel" style={{ flex: '0 0 auto', padding: '15px', overflow: 'hidden', display: 'flex', flexDirection: 'column', position: 'relative' }}>
                        <div className="panel-title">PATIENT DETAILS</div>
                        {authError ? (
                            <div style={{
                                marginTop: '20px',
                                padding: '15px',
                                border: '1px solid var(--text-alert)',
                                backgroundColor: 'rgba(255, 42, 42, 0.1)',
                                color: 'var(--text-alert)',
                                textAlign: 'center',
                                fontSize: '0.8rem',
                                lineHeight: '1.5'
                            }}>
                                ⚠️ SECURITY OVERRIDE REQUIRED<br />
                                <br />
                                {authError}
                            </div>
                        ) : patientInfo ? (
                            <>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginBottom: '10px' }}>[DECRYPTED PAYLOAD]</div>
                                <PatientPayload />

                                <div style={{ marginTop: '10px', fontSize: '0.70rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>PATIENT ID:</span><span>PT-{patientInfo.patient_id}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>DEVICE:</span><span>{patientInfo.device}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>WARD:</span><span>{patientInfo.ward}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>TIMESTAMP:</span><span>{new Date().toISOString().split('.')[0].replace('T', ' ')} UTC</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}><span style={{ color: 'var(--text-muted)' }}>NAME:</span><span>{patientInfo.name}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>AGE / SEX:</span><span>{patientInfo.age} / {patientInfo.sex}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>BLOOD GROUP:</span><span>{patientInfo.blood_group}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>ALLERGIES:</span><span>{patientInfo.allergies}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--text-muted)' }}>ADMITTED:</span><span>{new Date(patientInfo.admitted).toISOString().split('T')[0]}</span></div>

                                    <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px dashed var(--border-glow)' }}>
                                        <div style={{ color: 'var(--text-muted)', marginBottom: '5px' }}>DATA SOURCES (DB LINKS):</div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem' }}><span>CSV:</span><span style={{ color: 'var(--text-success)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>{patientInfo.csv_link}</span></div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6rem' }}><span>DAT:</span><span style={{ color: 'var(--text-success)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>{patientInfo.dat_link}</span></div>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div style={{ marginTop: '20px', color: 'var(--text-muted)', textAlign: 'center' }}>Querying Secure DB...</div>
                        )}
                    </div>
                </div>

                {/* CENTER - WAVES & 3D TWIN */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', gridArea: 'center' }}>
                    <div className="cyber-panel ecg-grid" style={{ flex: 2, position: 'relative', overflow: 'hidden' }}>
                        <div style={{ position: 'absolute', top: '15px', left: '15px', right: '15px', zIndex: 10, display: 'flex', justifyContent: 'space-between' }}>
                            <div className="panel-title" style={{ margin: 0 }}>REAL-TIME ECG TRACING</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-success)' }}>V1, V2, V3, V4, V5, V6</div>
                        </div>
                        <ECGWaveform waveData={chartData} />
                    </div>

                    <div className="cyber-panel heart-container" style={{ flex: 1, position: 'relative' }}>
                        <div className="panel-title" style={{ position: 'absolute', top: '15px', left: '15px', zIndex: 10 }}>
                            CARDIAC DIGITAL TWIN (3D RENDER)
                        </div>
                        <DigitalTwin3D riskScore={riskScore} />
                    </div>
                </div>

                {/* RIGHT SIDEBAR - ALERTS, MEDS, & RISK */}
                <div className="right-sidebar" style={{ display: 'flex', flexDirection: 'column', gap: '10px', gridArea: 'right' }}>
                    <div className="cyber-panel" style={{ flex: 1, padding: '15px', display: 'flex', flexDirection: 'column' }}>
                        <div className="panel-title">ALERT LOG</div>
                        <AlertLog
                            riskScore={riskScore}
                            scenario={scenario}
                            isMuted={isMuted}
                            setIsMuted={setIsMuted}
                            clinicalNote={clinicalNote}
                            isGeneratingNote={isGeneratingNote}
                            onGenerateNote={handleGenerateNote}
                        />
                    </div>

                    <div className="cyber-panel" style={{ padding: '15px', display: 'flex', flexDirection: 'column' }}>
                        <div className="panel-title">ADMINISTERED MEDICATION</div>
                        <div style={{ fontSize: '0.75rem', display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
                            {patientInfo && patientInfo.medications && patientInfo.medications.length > 0 ? (
                                patientInfo.medications.map((med, idx) => (
                                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <div><span style={{ color: 'var(--text-main)' }}>{med.name}</span><br /><span style={{ color: 'var(--text-muted)' }}>{med.dosage}</span></div>
                                        <span style={{ color: 'var(--text-main)' }}>{med.time_administered}</span>
                                    </div>
                                ))
                            ) : (
                                <div style={{ color: 'var(--text-muted)' }}>No medications on file.</div>
                            )}
                        </div>
                    </div>

                    <div className="cyber-panel" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontSize: '2.5rem', color: isCritical ? 'var(--text-alert)' : 'var(--text-main)', fontWeight: 'bold' }}>
                                {(riskScore * 100).toFixed(0)}%
                            </div>
                            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>HEART RISK RATE</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '1.2rem', color: 'var(--text-main)', letterSpacing: '2px' }}>PREDICTIVE</div>
                            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>AI MODEL STATUS</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* UPLOAD RESULT MODAL */}
            {uploadResults && uploadResults.length > 0 && (
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
                    <div className="cyber-panel" style={{ width: '800px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-base)', border: uploadResults.some(r => r.is_critical) ? '1px solid var(--text-alert)' : '1px solid var(--text-success)' }}>
                        <div style={{ borderBottom: '1px solid var(--border-glow)', padding: '15px' }}>
                            <h2 style={{ margin: 0, color: uploadResults.some(r => r.is_critical) ? 'var(--text-alert)' : 'var(--text-success)' }}>
                                {uploadResults.some(r => r.is_critical) ? "🚨 CRITICAL FINDINGS DETECTED IN BATCH" : "✅ ALL BATCH PATIENTS STABLE"}
                            </h2>
                            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '5px', textTransform: 'uppercase' }}>
                                OFFLINE BATCH INFERENCE RESULT (Live Background Stream Unaffected)
                            </div>
                        </div>

                        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto' }}>
                            {uploadResults.map((result, index) => (
                                <div key={index} style={{ border: `1px solid ${result.is_critical ? 'var(--text-alert)' : 'var(--text-success)'}`, padding: '15px', background: 'var(--bg-panel)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                        <div><span style={{ color: 'var(--text-muted)' }}>FILE ANALYZED:</span> {result.filename}</div>
                                        <div style={{ color: result.is_critical ? 'var(--text-alert)' : 'var(--text-success)', fontWeight: 'bold' }}>
                                            {result.alert}
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,229,255,0.05)', padding: '15px', borderLeft: '2px solid var(--text-main)', marginBottom: '10px' }}>
                                        <div>FUSION RISK SCORE:</div>
                                        <div style={{ fontSize: '2rem', color: result.is_critical ? 'var(--text-alert)' : 'var(--text-success)' }}>
                                            {(result.fusion_risk_score * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                    <div style={{ background: 'rgba(255,42,42,0.05)', padding: '15px', borderLeft: result.is_critical ? '2px solid var(--text-alert)' : '2px solid var(--text-success)' }}>
                                        <div style={{ color: 'var(--text-muted)', marginBottom: '5px' }}>COUNTERFACTUAL ENGINE:</div>
                                        <div style={{ color: 'var(--text-warning)' }}>{result.counterfactual}</div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div style={{ padding: '15px', textAlign: 'right', borderTop: '1px solid var(--border-glow)' }}>
                            <button onClick={() => setUploadResults(null)} style={{ background: 'transparent', color: 'var(--text-main)', border: '1px solid var(--text-main)', padding: '5px 15px', cursor: 'pointer' }}>
                                CLOSE ANALYSIS
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    )
}

export default App;
