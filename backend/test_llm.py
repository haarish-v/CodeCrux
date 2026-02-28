import asyncio
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

response = client.post(
    "/api/generate_clinical_note/",
    json={
        "patient_id": "100",
        "name": "Alex Mercer",
        "age": 45,
        "sex": "M",
        "device": "ECG-2000",
        "ward": "ICU Bed 4",
        "risk_score": 0.85,
        "is_critical": True,
        "medications": [
            {"name": "Epinephrine", "dosage": "1mg IV", "time_administered": "10:05 AM"}
        ],
        "vitals_snapshot": {
            "hr": 140,
            "spo2": 88,
            "map": 55,
            "resp": 32
        }
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
