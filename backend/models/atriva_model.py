import torch
import torch.nn as nn

class ECGEncoder(nn.Module):
    def __init__(self, sequence_length=60*360):
        # 60s @ 360Hz approx
        super(ECGEncoder, self).__init__()
        # CNN for feature extraction
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=15, stride=2, padding=7),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=7, stride=2, padding=3),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        
        # BiLSTM for temporal patterns
        self.lstm = nn.LSTM(input_size=32, hidden_size=128, num_layers=2, batch_first=True, bidirectional=True)
        # Bidirectional with hidden_size=128 gives 256-D output per timestep
        
    def forward(self, x):
        # x shape: (batch_size, channels=1, sequence_length)
        x = self.conv(x)
        
        # Reshape for LSTM: (batch_size, sequence_length, features=32)
        x = x.transpose(1, 2)
        
        lstm_out, (hn, cn) = self.lstm(x)
        
        # Take the final timestep output. 
        # lstm_out shape is (batch_size, seq_len, 256)
        final_embedding = lstm_out[:, -1, :] # 256-D vector
        
        return final_embedding

class VitalsEncoder(nn.Module):
    def __init__(self, input_dim=6):
        # Inputs: HR, SpO2, MAP, RESP, Temp, etc.
        super(VitalsEncoder, self).__init__()
        
        # MLP made using fully connected layers
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU()
            # The output is a 64-dimensional feature embedding
        )
        
    def forward(self, x):
        # x shape: (batch_size, input_dim=6)
        return self.mlp(x)

class AtrivaFusionNet(nn.Module):
    def __init__(self):
        super(AtrivaFusionNet, self).__init__()
        self.ecg_encoder = ECGEncoder()
        self.vitals_encoder = VitalsEncoder(input_dim=6)
        
        # Late fusion by concatenating the ECG 256-D embedding with the vitals 64-D embedding
        # Fused vector = 320 features
        
        self.classifier = nn.Sequential(
            nn.Linear(320, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid() # Outputs probability 0.0 to 1.0 (Risk Score Calculation)
        )
        
    def forward(self, ecg, vitals):
        ecg_vec = self.ecg_encoder(ecg)       # (batch_size, 256)
        vitals_vec = self.vitals_encoder(vitals) # (batch_size, 64)
        
        # Final Input Vector = [ECG_256 + Vitals_64] = 320 features
        fused_state = torch.cat((ecg_vec, vitals_vec), dim=1) # (batch_size, 320)
        
        risk_score = self.classifier(fused_state)
        return risk_score
