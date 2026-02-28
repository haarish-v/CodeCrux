import torch
import sys
import os
sys.path.append(r"C:\Codes\Codecrux\backend")
from models.atriva_model import AtrivaFusionNet

def test_model():
    print("Loading model...")
    device = torch.device('cpu')
    model = AtrivaFusionNet()
    try:
        model.load_state_dict(torch.load(r"C:\Codes\Codecrux\backend\atriva_model.pt", map_location=device))
        model.eval()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # Normal Patient
    ecg_normal = torch.randn(1, 1, 360*60) * 0.1
    vitals_normal = torch.tensor([[75.0, 98.0, 85.0, 16.0, 37.0, 120.0]], dtype=torch.float32)
    
    # Critical Patient (Code Blue scenario configured in train_eval.py)
    # The training setup added: np.random.normal(loc=[60, -15, -35, 15, -1, -50], scale=1)
    # Original base: [75, 98, 85, 16, 37, 120]
    # Distressed: [135, 83, 50, 31, 36, 70]
    ecg_critical = torch.randn(1, 1, 360*60) * 3.0
    vitals_critical = torch.tensor([[135.0, 83.0, 50.0, 31.0, 36.0, 70.0]], dtype=torch.float32)

    with torch.no_grad():
        score_normal = model(ecg_normal, vitals_normal).item()
        score_critical = model(ecg_critical, vitals_critical).item()

    print(f"Normal Vitals Output Score: {score_normal:.6f}")
    print(f"Critical Vitals Output Score: {score_critical:.6f}")

if __name__ == '__main__':
    test_model()
