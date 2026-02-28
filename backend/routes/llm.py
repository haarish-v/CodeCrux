from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import os

router = APIRouter()

# The user's provided Featherless Premium API Key
FEATHERLESS_API_KEY = "rc_02a00b6e2146dbe53cfd19360dc8fd52a7a445baf629875ab8d00ec3b92f052b"
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

# Initialize the Async OpenAI Client pointing to Featherless
client = AsyncOpenAI(
    api_key=FEATHERLESS_API_KEY,
    base_url=FEATHERLESS_BASE_URL
)

class ClinicalContext(BaseModel):
    patient_id: str
    name: str
    age: int
    sex: str
    device: str
    ward: str
    risk_score: float
    is_critical: bool
    medications: list
    vitals_snapshot: dict

@router.post("/api/generate_clinical_note/")
async def generate_clinical_note(context: ClinicalContext):
    try:
        # Construct the medications string
        meds_str = "\n".join([f"- {m['name']} ({m['dosage']}) at {m['time_administered']}" for m in context.medications]) if context.medications else "None on file."
        
        # Build the strict Medical System Prompt
        system_prompt = """
        You are an elite ICU Attending Physician. Your job is to write a concise, highly professional, and urgent Clinical Note based on the telemetry Data provided by the Aegis-Omni FusionNet AI system.
        
        Rules:
        1. Keep the note strictly under 4 sentences.
        2. Be clinical, objective, and urgent if the patient is critical.
        3. Reference the PyTorch Fusion Risk Score, their active medications, and their vitals to justify your assessment.
        4. Focus exclusively on the medical interpretation of the data. Do NOT use markdown. Do NOT introduce yourself.
        """
        
        user_prompt = f"""
        Patient: {context.name} (ID: {context.patient_id})
        Demographics: {context.age}yo {context.sex}
        Location: {context.ward}
        
        Current Vitals Snapshot:
        HR: {context.vitals_snapshot.get('hr', 'N/A')} bpm
        SpO2: {context.vitals_snapshot.get('spo2', 'N/A')} %
        MAP: {context.vitals_snapshot.get('map', 'N/A')} mmHg
        RESP: {context.vitals_snapshot.get('resp', 'N/A')} rpm
        
        PyTorch Fusion Risk Score: {context.risk_score * 100:.1f}% (Critical: {context.is_critical})
        
        Administered Medications:
        {meds_str}
        
        Write the Clinical Assessment Note:
        """

        response = await client.chat.completions.create(
            model="NousResearch/Meta-Llama-3-8B-Instruct", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        note = response.choices[0].message.content.strip()
        return {"note": note}
        
    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
