import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import wfdb
from torch.utils.data import Dataset, DataLoader
from models.atriva_model import AtrivaFusionNet

# Hyperparameters
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 0.001
ECG_SEQ_LEN = 360 * 60  # 60 sec ECG segment at 360Hz

class ICU_Dataset(Dataset):
    def __init__(self, data_root, num_samples=100):
        self.data_root = data_root
        self.num_samples = num_samples
        
        print("Initializing supervised time-to-event labeling simulation...")
        # In a real scenario, this involves heavy preprocessing (Bandpass filter, alignment)
        # We will load short snippets from mitdb and bidmc to form our 60s windows
        
        self.raw_ecg = self._load_ecg_snippet("100")
        self.raw_vitals_base = np.array([75, 98, 85, 16, 37.0, 120]) # HR, SpO2, MAP, RESP, TEMP, SBP
        
    def _load_ecg_snippet(self, rec_name):
        try:
            path = os.path.join(self.data_root, "mitdb", rec_name)
            record = wfdb.rdrecord(path, sampto=ECG_SEQ_LEN * 2) # load a bit more
            return record.p_signal[:, 0]
        except Exception as e:
            print(f"Error loading {rec_name}: {e}")
            return np.zeros(ECG_SEQ_LEN * 2)

    def __len__(self):
        return self.num_samples
        
    def __getitem__(self, idx):
        # We simulate the supervised time-to-event slicing here
        
        # Step 1: 60 sec ECG segment
        start_idx = idx * 10 
        ecg_window = self.raw_ecg[start_idx : start_idx + ECG_SEQ_LEN]
        
        if len(ecg_window) < ECG_SEQ_LEN:
             # Padding just in case
             ecg_window = np.pad(ecg_window, (0, ECG_SEQ_LEN - len(ecg_window)))
             
        # Step 2: Preprocess (Simulated bandpass & normalization)
        ecg_window = (ecg_window - np.mean(ecg_window)) / (np.std(ecg_window) + 1e-8)
        
        # Latest vitals (6 inputs)
        # If idx > 50, we label as "imminent Code Blue" (1) and distort vitals
        is_code_blue = 1.0 if idx > (self.num_samples // 2) else 0.0
        
        if is_code_blue:
            vitals = self.raw_vitals_base + np.random.normal(loc=[40, -10, -30, 10, -1, -40], scale=2)
            # Add arrhythmia to ECG
            ecg_window += np.sin(np.linspace(0, 100, ECG_SEQ_LEN)) * 2
        else:
            vitals = self.raw_vitals_base + np.random.normal(scale=1, size=(6,))
            
        # Convert to tensors
        ecg_tensor = torch.tensor(ecg_window, dtype=torch.float32).unsqueeze(0) # (1, seq_len)
        vitals_tensor = torch.tensor(vitals, dtype=torch.float32) # (6,)
        label = torch.tensor([is_code_blue], dtype=torch.float32)
        
        return ecg_tensor, vitals_tensor, label

def train_model():
    print("="*60)
    print("Initializing ATRIVA Multi-Modal Training Engine")
    print("Architecture: late fusion (ECG 256-D + Vitals 64-D = 320-D State Vector)")
    print("="*60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    # 1. Load Data
    data_dir = r"C:\Codes\Codecrux\data"
    dataset = ICU_Dataset(data_dir, num_samples=64) # Small batch for fast presentation test
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # 2. Setup Model
    model = AtrivaFusionNet().to(device)
    criterion = nn.BCELoss() # Binary Cross Entropy for Probability (Risk Score)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # 3. Training Loop
    model.train()
    for epoch in range(EPOCHS):
        epoch_loss = 0.0
        for batch_idx, (ecg, vitals, labels) in enumerate(dataloader):
            ecg, vitals, labels = ecg.to(device), vitals.to(device), labels.to(device)
            
            # Forward pass (Step 3 & 4 inside model)
            optimizer.zero_grad()
            risk_scores = model(ecg, vitals)
            
            # Step 5: Risk Score Calculation
            loss = criterion(risk_scores, labels)
            
            # Backward pass & Optimize
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        print(f"Epoch [{epoch+1}/{EPOCHS}] - Loss: {epoch_loss/len(dataloader):.4f}")
        
    # 4. Save the trained weights for the demo
    save_path = "atriva_fusion_weights.pth"
    torch.save(model.state_dict(), save_path)
    print("="*60)
    print(f"✅ Training Complete. Models weights saved to {save_path}")
    print("Ready for real-time inference.")
    print("="*60)

if __name__ == "__main__":
    train_model()
