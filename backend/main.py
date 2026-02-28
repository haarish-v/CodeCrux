from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import telemetry, predict_realtime, patient, llm

app = FastAPI(
    title="ATRIVA Omniscient Engine",
    description="Backend for the ATRIVA ICU telemetry dashboard",
    version="1.0.0"
)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(telemetry.router)
app.include_router(predict_realtime.router)
app.include_router(patient.router)
app.include_router(llm.router)

@app.get("/")
async def root():
    return {"status": "Aegis-Omni systems nominal", "version": "1.0.0"}
