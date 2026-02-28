import torch
import torch.nn as nn

# 1. ECGNet: Deep CNN for continuous wave embedding (360Hz)
class ECGNet(nn.Module):
    def __init__(self, embedding_dim=32):
        super().__init__()
        self.conv_blocks = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=15, stride=2, padding=7),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=7, stride=2, padding=3),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        self.fc = nn.Linear(64, embedding_dim)

    def forward(self, x):
        # x shape: (batch, channels=1, sequence_len=e.g. 500)
        features = self.conv_blocks(x)
        features = features.squeeze(-1)
        return self.fc(features)

# 2. VitalsGRU: Temporal RNN for numerical sequences (1Hz/minutes resolution)
class VitalsGRU(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64, embedding_dim=32):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=2, batch_first=True)
        self.fc = nn.Linear(hidden_dim, embedding_dim)

    def forward(self, x):
        # x shape: (batch, sequence_len=e.g. 60, input_dim=Vitals: HR/SpO2/MAP/Resp)
        output, hn = self.gru(x)
        # We take the output of the last hidden state of the sequence
        return self.fc(hn[-1])

# 3. FusionNet: Combining High-Freq and Low-Freq temporal embeddings for 'Code Blue' Prediction
class FusionNet(nn.Module):
    def __init__(self, ecg_model, vitals_model, fusion_dim=64):
        super().__init__()
        self.ecg_model = ecg_model
        self.vitals_model = vitals_model
        
        # We concatenate a 32-dim ECG and 32-dim Vitals embedding = 64
        self.classifier = nn.Sequential(
            nn.Linear(32 + 32, fusion_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(fusion_dim, 1),
            nn.Sigmoid() # Outputs Risk Score 0.0 to 1.0
        )

    def forward(self, ecg_x, vitals_x):
        ecg_emb = self.ecg_model(ecg_x)
        vitals_emb = self.vitals_model(vitals_x)
        fused = torch.cat((ecg_emb, vitals_emb), dim=1)
        risk_score = self.classifier(fused)
        return risk_score

# 4. DigitalTwinSimulator (LSTM) for predicting future patient trajectory (Next 60s)
class DigitalTwinSimulator(nn.Module):
    def __init__(self, vitals_dim=4, hidden_dim=64, future_steps=60):
        super().__init__()
        self.future_steps = future_steps
        self.lstm = nn.LSTM(vitals_dim, hidden_dim, num_layers=2, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, vitals_dim)

    def forward(self, x):
        """Autoregressive prediction of the next trajectories based on history."""
        batch_size = x.size(0)
        outputs = []
        
        # Encode history
        lstm_out, (hn, cn) = self.lstm(x)
        
        # Take the last known step as the first input for autoregression
        curr_input = x[:, -1, :].unsqueeze(1)
        
        # Autoregressive generation
        for _ in range(self.future_steps):
            out, (hn, cn) = self.lstm(curr_input, (hn, cn))
            pred = self.fc_out(out)
            outputs.append(pred)
            curr_input = pred # feed prediction as next input
            
        return torch.cat(outputs, dim=1)
