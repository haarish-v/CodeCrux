import React, { useState } from 'react';

export const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const host = window.location.hostname;
            const response = await fetch(`http://${host}:8000/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                onLogin(data); // Pass token and user details to parent
            } else {
                const errData = await response.json();
                setError(errData.detail || "Login failed");
            }
        } catch (e) {
            console.error(e);
            setError("Connection to secure server failed.");
        }
    };

    return (
        <div style={{
            height: '100vh',
            width: '100vw',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: 'var(--bg-base)',
            color: 'var(--text-main)'
        }}>
            <div className="cyber-panel" style={{
                padding: '40px',
                width: '400px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
                border: '1px solid var(--text-main)',
                boxShadow: '0 0 15px rgba(0, 229, 255, 0.2)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '10px' }}>
                    <h1 style={{ margin: 0, letterSpacing: '4px', fontSize: '2rem' }}>ATRIVA</h1>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', letterSpacing: '2px' }}>SECURE ACCESS TERMINAL</div>
                </div>

                {error && (
                    <div style={{
                        padding: '10px',
                        border: '1px solid var(--text-alert)',
                        backgroundColor: 'rgba(255, 42, 42, 0.1)',
                        color: 'var(--text-alert)',
                        fontSize: '0.8rem',
                        textAlign: 'center'
                    }}>
                        [SEC ERROR] {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <div>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>OPERATOR ID</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                marginTop: '5px',
                                backgroundColor: 'var(--bg-panel)',
                                border: '1px solid var(--border-glow)',
                                color: 'var(--text-main)',
                                outline: 'none'
                            }}
                            required
                        />
                    </div>
                    <div>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CREDENTIALS</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                marginTop: '5px',
                                backgroundColor: 'var(--bg-panel)',
                                border: '1px solid var(--border-glow)',
                                color: 'var(--text-main)',
                                outline: 'none'
                            }}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        style={{
                            padding: '12px',
                            marginTop: '10px',
                            backgroundColor: 'transparent',
                            border: '1px solid var(--text-main)',
                            color: 'var(--text-main)',
                            cursor: 'pointer',
                            letterSpacing: '2px',
                            fontWeight: 'bold',
                            transition: 'all 0.3s'
                        }}
                        onMouseOver={(e) => { e.target.style.backgroundColor = 'var(--text-main)'; e.target.style.color = '#000'; }}
                        onMouseOut={(e) => { e.target.style.backgroundColor = 'transparent'; e.target.style.color = 'var(--text-main)'; }}
                    >
                        AUTHENTICATE
                    </button>

                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '20px', lineHeight: '1.5' }}>
                        AVAILABLE ROLES FOR TESTING:<br />
                        - chief (pass: chief123) -&gt; ALL access<br />
                        - specialist1 (pass: spec123) -&gt; 100, 105<br />
                        - specialist2 (pass: spec123) -&gt; 200, 231<br />
                        - nurse (pass: nurse123) -&gt; NO sensitive access
                    </div>
                </form>
            </div>
        </div>
    );
};
