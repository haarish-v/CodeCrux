# In a true deployment, this script would run as the Flwr Client on the Hospital Node.
# We create a simulation wrapper for the Startup presentation.

import torch
import torch.nn as nn
from models.fusion import ECGNet, VitalsGRU, FusionNet

class FederatedSimulator:
    def __init__(self):
        self.global_model = self._initialize_global_model()
        self.clients = ["Apollo_ICU", "Fortis_ICU", "Max_ICU"]
        print("Initialized ATRIVA Federated Global Server")

    def _initialize_global_model(self):
        ecg = ECGNet()
        vitals = VitalsGRU()
        fusion = FusionNet(ecg, vitals)
        return fusion
        
    def perform_federated_round(self):
        """Simulates one round of Federated Averaging (FedAvg)."""
        print("Starting FedAvg Round 1...")
        
        client_weights = []
        for client in self.clients:
            print(f"[{client}] Requesting local training on raw patient data...")
            # Simulate local training by copying global model and adding slight noise
            local_model = self._initialize_global_model()
            local_model.load_state_dict(self.global_model.state_dict())
            
            with torch.no_grad():
                for param in local_model.parameters():
                    # simulates an update step
                    param.add_(torch.randn(param.size()) * 0.001)
                    
            client_weights.append(local_model.state_dict())
            print(f"[{client}] Training complete. Encrypted weights sent to Global Server.")
            
        # FedAvg Aggregation on Global Server
        print("Aggregating weights on Central Server...")
        aggregated_weights = {}
        for key in client_weights[0].keys():
            weights_sum = torch.stack([client[key] for client in client_weights], dim=0)
            aggregated_weights[key] = torch.mean(weights_sum, dim=0)
            
        self.global_model.load_state_dict(aggregated_weights)
        print("Global Model Updated Successfully with ZERO raw data transfer.")

if __name__ == "__main__":
    sim = FederatedSimulator()
    sim.perform_federated_round()
