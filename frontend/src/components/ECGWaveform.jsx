import React, { useRef, useEffect } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export const ECGWaveform = ({ waveData }) => {
    // Setup ChartJS options to look like an oscilloscope/ECG monitor
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        animation: false, // Turn off for performance with high freq streaming
        elements: {
            point: {
                radius: 0 // Hide points, just line
            },
            line: {
                borderWidth: 1.5,
                tension: 0.1, // Slight curve, but mostly sharp for ECG QRS
            }
        },
        scales: {
            x: {
                display: false, // Hide X axis
                min: 0,
                max: 300 // Number of points to show on screen at once
            },
            y: {
                display: false, // Hide Y axis
                min: -1.5, // Typical mV range
                max: 1.5
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
        }
    };

    const data = {
        labels: Array.from({ length: 300 }, (_, i) => i),
        datasets: [
            {
                label: 'ECG',
                data: waveData || [], // We expect an array of numbers
                borderColor: '#00ffcc',
                backgroundColor: 'transparent',
            }
        ]
    };

    return (
        <div style={{ height: '100%', width: '100%', padding: '10px' }}>
            <Line options={options} data={data} />
        </div>
    );
};
