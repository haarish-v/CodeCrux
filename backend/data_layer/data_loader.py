import os
import wfdb
import numpy as np
import torch
import sys

# Ensure backend root is in path for model imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.atriva_model import AtrivaFusionNet

# A realistic Multi-Million Dollar AI platform needs robust data pipelines.
# We decouple the file reading from the streaming logic.

class PatientStreamer:
    def __init__(self, data_root=r"C:\Codes\Codecrux\data"):
        self.data_root = data_root
        
        # MIT-BIH (Arrhythmia) - High Frequency ECG (~360Hz)
        self.ecg_record_name = "100" 
        self.ecg_path = os.path.join(self.data_root, "mitdb", self.ecg_record_name)
        
        # BIDMC (ICU) - Lower Frequency Vitals & Numerics (~125Hz / 1Hz)
        self.vitals_record_name = "bidmc01"
        self.vitals_path = os.path.join(self.data_root, "bidmc", self.vitals_record_name)
        
        self.scenario = "100"
        
        self.device = torch.device('cpu')
        self.model = AtrivaFusionNet()
        try:
            self.model.load_state_dict(torch.load("atriva_model.pt", map_location=self.device))
            self.model.eval()
            print("✅ DataLoader connected to PyTorch Live Inference Engine.")
        except Exception as e:
            print(f"⚠️ Warning: DataLoader could not map weights: {e}")
            
        self._load_records()

    def _load_records(self):
        """Loads WFDB records into memory for fast streaming."""
        try:
            print(f"Loading ECG from {self.ecg_path}")
            self.ecg_record = wfdb.rdrecord(self.ecg_path)
            # Use MLII lead (usually channel 0)
            self.ecg_signal = self.ecg_record.p_signal[:, 0]
            self.ecg_fs = self.ecg_record.fs # e.g. 360Hz
            
            print(f"Loading Vitals from {self.vitals_path}")
            self.vitals_record = wfdb.rdrecord(self.vitals_path)
            
            # Note: BIDMC has signals like RESP, PLETH, V (ECG II), ABP.
            # We map channel names to robust keys.
            sig_names = self.vitals_record.sig_name
            
            self.vitals_signals = {}
            for i, name in enumerate(sig_names):
                self.vitals_signals[name] = self.vitals_record.p_signal[:, i]
                
            self.vitals_fs = self.vitals_record.fs # e.g. 125Hz
            
            self.total_seconds = min(len(self.ecg_signal) / self.ecg_fs, 
                                     len(self.vitals_signals.get('ABP', [])) / self.vitals_fs if 'ABP' in self.vitals_signals else float('inf'))
            print(f"Records loaded. Synthesizing {self.total_seconds:.1f} seconds of coupled data.")
            
        except Exception as e:
            print(f"Error loading records: {e}")
            self.ecg_signal = np.zeros(3600)
            self.ecg_fs = 360
            self.vitals_signals = {}
            self.vitals_fs = 125

    def set_scenario(self, scenario):
        """Updates pointers to load different patient profiles based on scenario."""
        self.scenario = scenario
        if scenario.isdigit():
             self.ecg_record_name = scenario
             self.ecg_path = os.path.join(self.data_root, "mitdb", self.ecg_record_name)
        elif scenario == 'critical':
             self.ecg_record_name = "200" 
             self.ecg_path = os.path.join(self.data_root, "mitdb", self.ecg_record_name)
        elif scenario == 'stable':
             self.ecg_record_name = "100" 
             self.ecg_path = os.path.join(self.data_root, "mitdb", self.ecg_record_name)
        
        # Trigger generator reset
        self.reset_stream = True
        
        # Reload memory
        self._load_records()
        return {"status": "success", "scenario": scenario, "ecg_loaded": self.ecg_record_name}
        
    def stream_patient_data(self, chunk_duration_sec=0.05):
        """
        Generator predicting how the ATRIVA backend sends real-time fused telemetry.
        Reads sequential chunks of the loaded arrays.
        """
        ecg_chunk_size = int(self.ecg_fs * chunk_duration_sec)
        vitals_chunk_size = int(self.vitals_fs * chunk_duration_sec)
        
        current_time_sec = 0.0
        
        ecg_len = len(self.ecg_signal)
        
        ecg_idx = 0
        vitals_idx = 0
        
        # Simulate base vital numerics since WFDB usually stores raw waves
        # We extract 'numerics' like MAP or HR from the waves, or just simulate
        # the derived features if numerics aren't in the .dat
        base_hr = 75
        base_spo2 = 98
        base_map = 85
        base_resp = 16
        
        # Initialize EMA (Exponential Moving Average) state for smooth visuals
        if not hasattr(self, 'ema_risk_score'):
            self.ema_risk_score = 0.15 # start low default
            
        while ecg_idx + ecg_chunk_size < ecg_len:
            
            # Immediately reset streaming pointers if the user uploads a new scenario file
            if getattr(self, 'reset_stream', False):
                ecg_idx, vitals_idx, current_time_sec = 0, 0, 0.0
                self.reset_stream = False
            
            ecg_chunk = self.ecg_signal[ecg_idx:ecg_idx + ecg_chunk_size].tolist()
            
            # Provide high-freq pleth (SpO2 wave) if available, otherwise mock it
            if 'PLETH' in self.vitals_signals and len(self.vitals_signals['PLETH']) > vitals_idx + vitals_chunk_size:
                pleth_chunk = self.vitals_signals['PLETH'][vitals_idx:vitals_idx + vitals_chunk_size].tolist()
            else:
                pleth_chunk = []
                
            ecg_idx += ecg_chunk_size
            vitals_idx += vitals_chunk_size
            current_time_sec += chunk_duration_sec
            
            # Smooth physiological interpolation towards target states
            if self.scenario in ['200', '231', 'critical']:
                target_hr, target_spo2, target_map, target_resp = 135.0, 84.0, 52.0, 28.0
            else:
                target_hr, target_spo2, target_map, target_resp = 75.0, 98.0, 85.0, 16.0
                
            base_hr += (target_hr - base_hr) * 0.01 + np.random.normal(0, 0.1)
            base_spo2 += (target_spo2 - base_spo2) * 0.01 + np.random.normal(0, 0.05)
            base_map += (target_map - base_map) * 0.01 + np.random.normal(0, 0.1)
            base_resp += (target_resp - base_resp) * 0.01 + np.random.normal(0, 0.05)

            # --- LIVE PYTORCH INFERENCE OVER SLIDING WINDOW ---
            window_end = ecg_idx
            window_start = max(0, window_end - int(60 * self.ecg_fs))
            
            ecg_window = self.ecg_signal[window_start:window_end]
            if len(ecg_window) < int(60 * self.ecg_fs):
                 pad_len = int(60 * self.ecg_fs) - len(ecg_window)
                 ecg_window = np.pad(ecg_window, (pad_len, 0), 'constant', constant_values=0)
                 
            # CRITICAL: Normalize the sliding window according to PyTorch training baseline logic
            ecg_window = (ecg_window - np.mean(ecg_window)) / (np.std(ecg_window) + 1e-8)
                 
            # Convert 60-second window to tensor
            ecg_tensor = torch.tensor(ecg_window, dtype=torch.float32).view(1, 1, -1).to(self.device)
            # Vitals vector: [HR, SpO2, MAP, RESP, Temp, Systolic]
            vitals_tensor = torch.tensor([[base_hr, base_spo2, base_map, base_resp, 37.0, 120.0]], dtype=torch.float32).to(self.device)
            
            # Run model architecture continuously on stream
            with torch.no_grad():
                raw_risk_score = self.model(ecg_tensor, vitals_tensor).item()
                
            # Apply EMA to smooth the risk score for presentation
            self.ema_risk_score = self.ema_risk_score * 0.95 + float(max(0.01, min(0.99, raw_risk_score))) * 0.05

            yield {
                "timestamp": current_time_sec,
                "ecg_wave": ecg_chunk,
                "pleth_wave": pleth_chunk,
                "vitals": {
                    "HR": int(np.clip(base_hr, 40, 180)),
                    "SpO2": int(np.clip(base_spo2, 60, 100)),
                    "MAP": int(np.clip(base_map, 30, 120)),
                    "RESP": int(np.clip(base_resp, 8, 40))
                },
                "ai_insight": {
                    "fusion_risk_score": float(self.ema_risk_score),
                    "cardiac_contractility": float(max(0.2, 1.0 - self.ema_risk_score)), 
                    "respiratory_efficiency": float(max(0.3, 1.0 - self.ema_risk_score * 1.2))
                }
            }
